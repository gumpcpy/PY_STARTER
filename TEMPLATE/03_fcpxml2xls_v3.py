'''
Author: gumpcpy gumpcpy@gmail.com
Date: 2023-07-19 21:17:42
LastEditors: gumpcpy gumpcpy@gmail.com
LastEditTime: 2024-01-29 22:43:59
Description: 
命令行版本
pip3 install pandas
pip3 install openpyxl
輸入一個fcpxmld1.10，輸入一個csv或者excel，第一個欄位是RAW name第二個欄位是Camera Name想放的資料
會讀取fcpxml之後，把每一個resources> asset name找出，然後比對 csv裡的raw name找到的話，在 asset> metadata下面加一個
<md key="com.apple.proapps.mio.cameraName" value="sc00-01-EL-OK"/>其中的value就是我的第二個欄位cameraName想要放的值

'''
import os,sys
import csv
# from xml.etree.ElementTree import ElementTree,Element
import xml.etree.ElementTree as ET
import pandas as pd


class FCPXML2EXCEL_CORE():

    excel_file_path = ""
    xmld_path = ""
    info_fcpxml_path = ""
    fps = 24

    def __init__(self, **thePath):

        if os.path.isdir(thePath['xmld_path']):
            self.xmld_path = thePath['xmld_path']
            self.info_fcpxml_path = os.path.join(self.xmld_path, 'info.fcpxml')

            root, extension = os.path.splitext(self.xmld_path)
            self.excel_file_path = root + '.xlsx'
            print(f"寫入的excel:{self.excel_file_path}")

        else:
            print("Please Choose fcpxmld File")
            return False

    def convert_to_timecode(self, time_expression, fps=24):

        if time_expression.find("/") >= 0:  # 通常是3234343/2400s這樣，但也有3599s這種
            # 将时间表达式分割成分子和分母部分
            numerator, denominator = map(int, time_expression[:-1].split('/'))

            # 计算总帧数
            total_frames = (fps * numerator) // denominator

        else:
            total_frames = int(time_expression[:-1]) * fps

        # 计算小时、分钟和秒数
        seconds = total_frames // fps
        frames = total_frames % fps
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)

        # 格式化为时间码字符串（HH:MM:SS:FF）
        timecode = f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"

        return timecode

        # 使用示例
        # time_expression = '78189310/2400s'
        # fps = 24
        # timecode = convert_to_timecode(time_expression, fps)
        # print("转换后的时间码:", timecode)

    def read_xml_write_xls(self):

        tree = ET.parse(self.info_fcpxml_path)
        root = tree.getroot()

        project = root.find('.//project')
        sequence = project.find('.//sequence')
        spine = sequence.find('.//spine')

        data = {'Tag Name': [], 'Name': [],
                'Note': [], 'Raw Name': [], 'Offset': []}

        different_tag = []
        for child in spine:  # sequence > spine
            different_tag.append(child.tag)

        different_tag = list(set(different_tag))
        print("本fcpxmld出現的標籤有:")
        print(different_tag)
        print(f"處理的標籤有 sync-clip, clip, asset-clip, ref-clip, video 四種")
        print(f"若有新的標籤出現，會需要再做處理")

        '''
            firstly, get resources

        '''
        resourcesAssets = {'ID' : [] , 'Asset' : []}
        resources = root.find('.//resources')
        for child in resources:
            if child.tag == 'media':
                theId = child.get('id')
                # could be Sc01-001_005_04_B_NR_OK or B089_C014_0911NN
                theAsset = child.get('name')
                
                ref_clip = child.find('.//ref-clip')

                if ref_clip is not None:
                    theAsset = ref_clip.get('name') if ref_clip.get('name') is not None else ''
             
                resourcesAssets['ID'].append(theId)
                resourcesAssets['Asset'].append(theAsset)

                print("resources id:" + theId + " Raw:" + theAsset)

        '''
            END get resources
        '''

        i = 1
        for child in spine:  # sequence > spine
            # print(f"{str(i)} : {child.tag}")

            if child.tag == 'sync-clip':
                sync_clip_name = child.get('name')

                # print(f"INFO: {str(i)} : {sync_clip_name}")
                sync_clip_offset = child.get('offset')
                sync_clip_start_tc = self.convert_to_timecode(
                    sync_clip_offset, self.fps)
                note = child.find('note').text if child.find(
                    'note') is not None else ''
                asset_clip_name = child.find(
                    './/asset-clip').get('name') if child.find('.//asset-clip') is not None else ''
                # print("sync-clip=" + sync_clip_name + " raw name=" + asset_clip_name)
                # 将数据添加到列表中
                data['Tag Name'].append('sync-clip')
                data['Name'].append(sync_clip_name)
                data['Note'].append(note)
                data['Raw Name'].append(asset_clip_name)
                data['Offset'].append(sync_clip_start_tc)

                i += 1

            elif child.tag == 'clip':
                sync_clip_name = child.get('name')
                sync_clip_offset = child.get('offset')
                sync_clip_start_tc = self.convert_to_timecode(
                    sync_clip_offset, self.fps)

                # 将数据添加到列表中
                data['Tag Name'].append('clip')
                data['Name'].append(sync_clip_name)
                data['Note'].append('')
                data['Raw Name'].append('')
                data['Offset'].append(sync_clip_start_tc)

                i += 1

            elif child.tag == 'asset-clip':
                sync_clip_name = child.get('name')
                sync_clip_offset = child.get('offset')
                sync_clip_start_tc = self.convert_to_timecode(
                    sync_clip_offset, self.fps)

                metadata_element = child.find('.//metadata')

                if metadata_element is not None:
                    asset_clip_name = metadata_element.find(
                        './/md').get('value') if metadata_element.find('.//md') is not None else ''
                else:
                    asset_clip_name = ''

                # asset_clip_name = child.find('.//metadata').find('.//md').get('value') if child.find('.//metadata').find('.//md').get('value') is not None else ''
                # 将数据添加到列表中
                data['Tag Name'].append('asset-clip')
                data['Name'].append(sync_clip_name)
                data['Note'].append('')
                data['Raw Name'].append(asset_clip_name)
                data['Offset'].append(sync_clip_start_tc)

                i += 1

            elif child.tag == 'video':
                sync_clip_name = child.get('name')
                sync_clip_offset = child.get('offset')
                sync_clip_start_tc = self.convert_to_timecode(
                    sync_clip_offset, self.fps)
                
                data['Tag Name'].append('asset-clip')
                data['Name'].append(sync_clip_name)
                data['Note'].append('')
                data['Raw Name'].append('')
                data['Offset'].append(sync_clip_start_tc)

                i += 1


            # elif child.tag == 'gap' :
            #     sync_clip_name = child.get('name')
            #     sync_clip_offset = child.get('offset')
            #     sync_clip_start_tc = self.convert_to_timecode(sync_clip_offset,self.fps)

            #     # 将数据添加到列表中
            #     data['Tag Name'].append('gap')
            #     data['Name'].append(sync_clip_name)
            #     data['Note'].append('')
            #     data['Raw Name'].append('')
            #     data['Offset'].append(sync_clip_start_tc)

                # i += 1

            elif child.tag == 'ref-clip':
                sync_clip_name = child.get('name')

                # print("ref clip name=" + sync_clip_name)
                
                sync_clip_offset = child.get('offset')
                sync_clip_start_tc = self.convert_to_timecode(
                    sync_clip_offset, self.fps)
                
                
                asset_clip_name = ''
                theRefId = child.get('ref') # r2
                # find ref in resources
                if theRefId in resourcesAssets['ID']:
                    index_of_id = resourcesAssets['ID'].index(theRefId)
                    asset_clip_name = resourcesAssets['Asset'][index_of_id]                    

                # 将数据添加到列表中
                data['Tag Name'].append('ref-clip')
                data['Name'].append(sync_clip_name)
                data['Note'].append('')
                data['Raw Name'].append(asset_clip_name)
                data['Offset'].append(sync_clip_start_tc)

                i += 1

        # 创建DataFrame
        df = pd.DataFrame(data)

        # 将DataFrame写入Excel文件
        df.to_excel(self.excel_file_path, index=False)

        print(f"不包含gap共有 {str(i)} 筆資料已經寫入同路徑的Excel")

        return True
    

if len(sys.argv) < 2:
	print("Please Indicate [FCPXMLD Path]")
	sys.exit()

thePath = {}
thePath['xmld_path'] = sys.argv[1]

# excel_file_path = ""
# xmld_path = ""
info_fcpxml_path = ""
fps = 24

t = FCPXML2EXCEL_CORE(**thePath)
t.read_xml_write_xls()      
