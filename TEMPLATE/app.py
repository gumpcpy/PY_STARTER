import os
import sys
from pathlib import Path
import json
import uuid

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.responses import JSONResponse, Response
from extract.extract import Extract
from fastapi.encoders import jsonable_encoder

import uvicorn

app = FastAPI()

from utils.logging_config import configure_logging

logger = configure_logging(__name__)

# 在配置后立即添加一条测试日志
logger.info("日志系统已初始化")

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}


def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


async def img2json(file_path: str, correct: bool = True):
    try:
        logger.info(
            f"尝试使用模型: {config.LLM_MODEL} 和 OCR 引擎: {config.OCR_ENGINE}"
        )
        results = Extract(
            llm_type=config.LLM_ENGIN,
            llm_model=config.LLM_MODEL,
            ocr_engine=config.OCR_ENGINE,
        ).extract(str(file_path),correct)

        if results is None:
            logger.info(
                f"尝试使用模型: {config.LLM_MODEL_ALTER} 和 OCR 引擎: {config.OCR_ENGINE}"
            )
            results = Extract(
                llm_type=config.LLM_ENGIN_ALTER,
                llm_model=config.LLM_MODEL_ALTER,
                ocr_engine=config.OCR_ENGINE,
            ).extract(str(file_path),correct)

        if results is None:
            logger.info(
                f"尝试使用模型: {config.LLM_MODEL_ALTER} 和 OCR 引擎: {config.OCR_ENGINE_ALTER}"
            )
            results = Extract(
                llm_type=config.LLM_ENGIN_ALTER,
                llm_model=config.LLM_MODEL_ALTER,
                ocr_engine=config.OCR_ENGINE_ALTER,
            ).extract(str(file_path),correct)

        if results is None:
            raise HTTPException(status_code=400, detail="无结果")

        # 使用 jsonable_encoder 处理结果
        encoded_results = jsonable_encoder(results)

        # 使用 json.dumps 进行自定义 JSON 编码
        json_str = json.dumps(encoded_results, ensure_ascii=False, indent=4)

        # 返回格式化的JSON响应
        return Response(
            content=json_str,
            media_type="application/json",
            headers={"Content-Type": "application/json; charset=utf-8"},
        )

    except Exception as e:
        logger.exception(f"处理文件 {file_path} 时发生错误")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@app.post("/process")
async def process_file(file_path: str = Body(..., embed=True),correct: bool = Body(True, embed=True)):
    if not file_path:
        raise HTTPException(status_code=400, detail="缺少 file_path")

    file_path = Path(file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件未找到")

    logger.info(f"准备OCR文件: {file_path}")
    try:
        result = await img2json(file_path,correct)
        logger.info(f"文件OCR完成: {file_path}")
        return result
    except Exception as e:
        logger.error(f"处理文件 {file_path} 时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@app.post("/upload")
async def upload_file(file_path: str = Body(..., embed=True)):
    if not file_path:
        raise HTTPException(status_code=400, detail="缺少 file_path")

    file_path = Path(file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件未找到")

    if not allowed_file(file_path.name):
        raise HTTPException(status_code=400, detail="文件类型不允许")

    patient_id = file_path.parent.name
    if not patient_id:
        raise HTTPException(status_code=400, detail="缺少 patient_id")

    logger.info(f"正在处理上传文件: {file_path}")
    try:
        unique_filename = f"{uuid.uuid4().hex}{file_path.suffix.lower()}"
        patient_folder = Path(config.UPLOAD_FOLDER) / patient_id
        patient_folder.mkdir(parents=True, exist_ok=True)
        new_file_path = patient_folder / unique_filename

        file_path.rename(new_file_path)

        logger.info(f"文件上传成功: {new_file_path}")
        return JSONResponse(
            content={"message": "文件上传成功", "file_path": str(new_file_path)},
            status_code=200,
        )
    except Exception as e:
        logger.error(f"处理上传文件 {file_path} 时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="localhost", port=5000, reload=True, reload_dirs=["."])
