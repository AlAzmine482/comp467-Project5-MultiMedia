import argparse
import csv
import os
import subprocess
import cv2
import pymongo
import re
import xlsxwriter
from frameioclient import FrameioClient
#from frameio_upload import upload_items_to_project
import requests


producer = []
operator = []
job = []
notes = []

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process Baselight and Xytech files.')
    parser.add_argument("-b", "--baselight", required=True, help="Path to the Baselight file")
    parser.add_argument("-x", "--xytech", required=True, help="Path to the Xytech file")
    parser.add_argument("-p", "--process", required=False, help="Path to the Xytech file")
    parser.add_argument("-o","--output", choices=["csv", "xls"])
    return parser.parse_args()

def generate_ranges(numbers):
    ranges = []
    start = end = numbers[0]
    for num in numbers[1:]:
        if num == end + 1:
            end = num
        else:
            ranges.append((start, end))
            start = end = num
    ranges.append((start, end))
    return ranges


def read_baselight(baselight_file):
    baselight_data = {}
    with open(baselight_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line:  # Check if the line is not empty
                parts = line.split()
                if len(parts) > 1:
                    location = parts[0]
                    #print(location)
                    file_name = os.path.basename(location)
                    frame_numbers = [int(part) for part in parts[1:] if part not in ['<null>', '<err>']]
                    ranges = generate_ranges(frame_numbers)
                    if location not in baselight_data:
                        baselight_data[location] = {'path': location, 'ranges': ranges}
                    else:
                        baselight_data[location]['ranges'].extend(ranges)
        
    return baselight_data

def read_xytech(xytech_file, baselight_data):
    
 
    xytech_data = {}
    with open(xytech_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("Producer:"):
                w = line.replace("Producer: ", "")
                stripn = w.strip('\n')
                producer.append(stripn)
                #print(producer)
            if line.startswith("Operator:"):
                operators = line.replace("Operator: ", "")
                stripopn = operators.strip('\n')
                operator.append(stripopn)
            if line.startswith('Job:'):
                jobrep = line.replace("Job: ", "") 
                jobsp = jobrep.strip('\n')
                job.append(jobsp)
            if line.startswith('Please '):
                notes.append(line)
                #print(notes)
            if line.startswith("/"):
                parts = line.split('/')
                location = "/".join(parts[2:])
                orgloc = "/".join(parts[1:])
                for baselight_location, baselight_info in baselight_data.items():
                    stripped_baselight_location = baselight_location.strip("/baselightfilesystem1/")
                    #print(stripped_baselight_location)
                    if location.endswith(stripped_baselight_location):
                        xytech_data[orgloc] = {'path': orgloc, 'ranges': baselight_info['ranges']}
                        break
        print("this is xytech")
    
    return xytech_data


def open_video(video_file, xytech_data, output):
    cap = cv2.VideoCapture(video_file)
    current_directory = os.getcwd()
    print(video_file)
 
    """output_dir = os.path.join(current_directory, 'frames')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    frame_number = 0
    frame_list= []
    
    while cap.isOpened():
        ret, frame = cap.read()
        # Break the loop if we have reached the end of the video
        if not ret:
            break

        # Save the current frame as an image
        frame_filename = os.path.join(output_dir, f'frame{frame_number:04d}.png')
        cv2.imwrite(frame_filename, frame)

        #frame_list.append(frame)

        frame_number += 1




    cap.release()
    cv2.destroyAllWindows()
   
    """
    frame_directory = os.path.join(current_directory, "frames")
    png_files = [f for f in os.listdir(frame_directory) if f.endswith('.png')]
    frame_pattern = re.compile(r'frame(\d{4})\.png')
    frame_list = [int(frame_pattern.search(f).group(1)) for f in png_files if frame_pattern.search(f)]
    max_frame_num = max(frame_list)
    print(max_frame_num)

   
    print("\n")
    fps = get_fps(video_file)
    print("\n")
    print("FPS: ",fps)
    lengthofvid = get_vid_length(video_file)
    print("\n")
    print("Length of video: ",lengthofvid)
    fpscheck = int(fps * lengthofvid)
    print("\n")
    print("FPSCHECK: ",fpscheck)
    testval = []

    xytech_frame_numbers = []
    for data in xytech_data.values():
        for start, end in data['ranges']:
            xytech_frame_numbers.extend(range(start, end + 1))

        # Convert xytech frame numbers to timecodes
    timecodes = convert_frames_to_timecodes(xytech_frame_numbers, fps)
    print("Timecodes:")
    for code in timecodes:
        print(code)
    #print("finally")

    #print("\n")
    print("\n",sorted(timecodes))

    
    if output == "csv": 
        print("CSV File output\n")
        with open("project3.csv", "w", newline="") as csvfile:
            fieldnames = ["Producer", "Operator", "Job", "Notes"]
            thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
            thewriter.writeheader()
            thewriter.writerow({"Producer": producer,
                                "Operator": operator,
                                "Job": job,
                                "Notes": notes})
            Write = csv.writer(csvfile)
            splitDR = ["Directory", "Frames"]
            lastWrite = csv.DictWriter(csvfile, fieldnames = splitDR)

            for path, data in xytech_data.items():
                ranges = data.get('ranges', [])  # Get the ranges, default to empty list if not found
                for start, end in ranges:
                    # Write each range on a separate row
                    range_str = f"{start}-{end}" if start != end else str(start)
                    lastWrite.writerow({"Directory": path, "Frames": range_str})
            

           
            #Write = csv.writer(csvfile)
            #csvfile.write("Location,Ranges,Timecode,Thumbnail\n")
    
    elif args.output == "xls":
        storestart =[]
        print("XLS output")
        workbook = xlsxwriter.Workbook("project3.xlsx")
        worksheet = workbook.add_worksheet()

        # Write headers for producer, operator, job, and notes
        worksheet.write(0, 0, "Producer")
        worksheet.write(0, 1, "Operator")
        worksheet.write(0, 2, "Job")
        worksheet.write(0, 3, "Notes")

        # Write headers for directory, frames, timecode, and thumbnail
        worksheet.write(3, 0, "Directory")
        worksheet.write(3, 1, "Frames")
        worksheet.write(3, 2, "Timecode")
        worksheet.write(3, 3, "Thumbnail")

        # Write data for producer, operator, job, and notes
        for i, value in enumerate(producer):
            worksheet.write(i + 1, 0, value)
        for i, value in enumerate(operator):
            worksheet.write(i + 1, 1, value)
        for i, value in enumerate(job):
            worksheet.write(i + 1, 2, value)
        for i, value in enumerate(notes):
            worksheet.write(i + 1, 3, value)

        # Write data for xytech_data
        row = len(producer) + 3  # Start from the next row after the headers and producer data
        """
        for path, data in xytech_data.items():
            ranges = data.get('ranges', [])  # Get the ranges, default to empty list if not found
            for start, end in ranges:
                # Write each range on a separate row along with its corresponding directory (path)
                range_str = f"{start}-{end}" if start != end else str(start)
                middle_number = (start + end) // 2
                storestart.append(middle_number)
                match_number = [start_val for start_val in storestart if start in frame_list]
                matchingpng_files = []
                
                worksheet.write(row, 0, path) 
                worksheet.write(row, 1, range_str)
                row += 1 
                start_timecode = convert_frames_to_timecodes([start], fps)[0]
                end_timecode = convert_frames_to_timecodes([end], fps)[0]
                timecode_str = f"{start_timecode} - {end_timecode}"
                worksheet.write(row, 2, timecode_str)
                
                # Insert thumbnail in its respective column
                
                
            
                for every in match_number:
                    matching_files = [f for f in os.listdir("C:/Users/Al Azmine/Chaja proj 2/frames/") if f.endswith(f'{str(every).zfill(4)}.png')]
                    matchingpng_files.extend(matching_files)
                
                thirdrow = 4
               
                for image_file in matchingpng_files:
                    image_path = "C:/Users/Al Azmine/Chaja proj 2/frames/" + image_file
                    worksheet.insert_image(thirdrow, 4 , image_path,{'x_scale': 0.1, 'y_scale': 0.1, 'width': 50, 'height': 30})
                    thirdrow +=1
            workbook.close()
            """
        for path, data in xytech_data.items():
            ranges = data.get('ranges', [])  # Get the ranges, default to empty list if not found
            for start, end in ranges:
                # Write each range on a separate row along with its corresponding directory (path)
                range_str = f"{start}-{end}" if start != end else str(start)
                 
                worksheet.write(row, 0, path) 
                worksheet.write(row, 1, range_str)
                
                start_timecode = convert_frames_to_timecodes([start], fps)[0]
                end_timecode = convert_frames_to_timecodes([end], fps)[0]
                timecode_str = f"{start_timecode} - {end_timecode}"
                worksheet.write(row, 2, timecode_str) 
                worksheet.set_column(row, 2, width=30)
                # Check if it's a range with more than one frame
                if start != end:
                    middle_number = (start + end) // 2
                    if middle_number <= max_frame_num:  # Check if the middle frame number is within the available frames
                        storestart.append(middle_number)  # Append the middle number to the list
                       
                        
                        
                        
                        # Insert thumbnail in its respective column
                        matching_files = [f for f in png_files if f.endswith(f'{str(middle_number).zfill(4)}.png')]
                        for image_file in matching_files:
                            image_path = os.path.join(frame_directory, image_file)
                            worksheet.insert_image(row, 3, image_path, {'x_scale': 0.1, 'y_scale': 0.1})
                            worksheet.set_row(row, height=76)
                            worksheet.set_column(3, 3, width=50)  # Increase column width
                row += 1

        workbook.close()
        
        #ffmpeg_command = f'ffmpeg -i {video_file} -vf "showinfo" -f null -'
        #output = subprocess.check_output(ffmpeg_command, shell=True, stderr=subprocess.STDOUT).decode()
       
        project_id = '23c8342b-c6f6-41ae-8d6c-645973b37aa9'
        #timecode_data = {"timecode": timecode_str}
        #range_data = {"range": range_str}

        mytoken = 'path_to_Token'
        #client = FrameioClient("ChajaToken")
        #client = FrameioClient("ChajaToken")
        #me = client.users.get_me()
        #print(me['id'])
    

        #url = "https://api.frame.io/v2/me"
        #headers = {"Authorization": "Bearer <ChajaToken>"}

        #requests.get(url,headers=headers)
        #client.assets.upload(project_id, timecode_data)
        #client.assets.upload(project_id, range_data)

        
        """      
                #row += 1  # Move to the next row for the next range
        url = f"https://app.frame.io/projects/23c8342b-c6f6-41ae-8d6c-645973b37aa9/items"
        #mytoken = 'fio-u-VW45z5e-LpRLFdM7_B1h3woDv-kfrmI9FJYmFchyiC-R2LZf9Z9a6ys3TXynK4-9'
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {mytoken}"
        }
        part = {
            "TimeCode": timecode_str,
            "ranges": range_str
        }

        # Make the request
        response = requests.post(url, json=part, headers=headers)

        # Check response status and handle errors
        if response.status_code == 200:
            print("Data uploaded successfully to Frame.io!")
        else:
            print("Failed to upload data to Frame.io. Status code:", response.status_code)
            print("Response:", response.text)
        
       
        # Prepare data for uploading items
        data = {
            "timestamps": timecode_str,
            "ranges_str": range_str
        }
        upload_items_to_project(project_id, mytoken, data)
        #print("after upload")"""   
        #upload_items_to_project(project_id, mytoken, timecode_str, range_str)
        #client = FrameioClient("ChajaToken")
      

        asset_id = "23c8342b-c6f6-41ae-8d6c-645973b37aa9"
        url = "https://api.frame.io/v2/assets/" + asset_id + "/b6609ff9-83b3-479d-821a-f51b3191e647"

        payload = {
        "parts": [
            {
            "number": 1,
            "size": "20000000000",
            "is_final": False
            },
            {
            "number": 2,
            "size": "15000000000",
            "is_final": False
            }
        ]
        }

        headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer <fio-u-VW45z5e-LpRLFdM7_B1h3woDv-kfrmI9FJYmFchyiC-R2LZf9Z9a6ys3TXynK4-9>"
        }

        response = requests.post(url, json=payload, headers=headers)

        data = response.json()
        print(data)
    
def upload_items_to_project(project_id, token, timecode_str, range_str):
    # Define the API endpoint
    api_base_url = "https://api.frame.io/v2"
    project_endpoint = f"{api_base_url}/projects/{project_id}/items"

    # Prepare data for uploading items
    data = {
        "timestamps": 2,
        "ranges_str": "1"
    }

    # Set request headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Make the POST request
    response = requests.post(project_endpoint, json=data, headers=headers)

    # Check the response status and handle errors
    if response.status_code == 200:
        print("Data uploaded successfully to Frame.io!")
    else:
        print(f"Failed to upload data to Frame.io. Status code: {response.status_code}")
        print("Response:", response.text)




def populate_mongodb(baselight_data, xytech_data):
    client = pymongo.MongoClient("localhost")
    mydb = client["mydatabase"]
    #print(client.list_database_names())
    mycollection = mydb["WeeklyQA"]
    collection2 = mydb["DBDUMP"]

    #print(mydb.list_collection_names())

    baselight_collection = mydb["Baselight"]
    baselight_collection.insert_many(baselight_data.values())

    # Populate Xytech collection
    xytech_collection = mydb["Xytech"]
    xytech_collection.insert_many(xytech_data.values())

def get_fps(video_path):
    cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v', '-of', 
           'default=noprint_wrappers=1:nokey=1', '-show_entries', 
           'stream=r_frame_rate', video_path]
    output = subprocess.check_output(cmd).decode('utf-8').strip()
    if '/' in output:  # Frame rate might be a ratio, so we compute it
        num, den = output.split('/')
        return float(num) / float(den)
    else:
        return float(output)

def get_vid_length(input):
    video = input
    command = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video]
    x = float(subprocess.check_output(command))
    return x

def convert_frames_to_timecodes(frames, fps):
    timecodes = []
    for frame in frames:
        total_seconds = frame / fps
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        deci_seconds = round((total_seconds - int(total_seconds)) * fps)
        timecodes.append(f"{hours:02d}:{minutes:02d}:{seconds:02d}:{deci_seconds:02d}")
    return timecodes

if __name__ == "__main__":
    args = parse_arguments()

    # Read Baselight file and generate dictionary of file name and frame ranges
    baselight_file_data = read_baselight(args.baselight)
    for file_name, data in baselight_file_data.items():
        print(f"{data['path']} {file_name}:", end=" ")
        for start, end in data['ranges']:
            if start == end:
                print(start, end=" ")
            else:
                print(f"{start}-{end}", end=" ")
        print()

    # Read XYTech file and match entries with Baselight data
    xytech_file_data = read_xytech(args.xytech, baselight_file_data)
    for file_path, data in xytech_file_data.items():
        print(f"{file_path}:", end=" ")
        for start, end in data['ranges']:
            if start == end:
                print(start, end=" ")
            else:
                print(f"{start}-{end}", end=" ")
        print()
    populate_mongodb(baselight_file_data, xytech_file_data)
    
    process_video_file = open_video(args.process, xytech_file_data, args.output)
   
    #print(xytech_file_data)
    



    
    #get the timecode then look for a clip within the timecode and clips filter it then upload to frame.io
