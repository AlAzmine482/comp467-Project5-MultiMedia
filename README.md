# comp467-Project5-MultiMedia
Reading Baselight, xytech, and video demo files and getting frames, pictures, and clips. Uploading to Frame.io. Pictures get insert into xlsxfile, paths, folders, and other frames to fix go to csv

In this project, We use argparse to parse text files and video files. After reading the data from the text files. You can uncomment the section below to generate the frames directory in your project folder. In the frame directory, it will create video frames according to duration. Then get the fps using ffprobe and get the duration of video. We multiply the fps and duration to check the fps. We call the function convert_frames_to_timecodes to get the total seconds which divides the frame and fps into hours, minutes seconds, and deci seconds. Then depending on the output it will generate a CSV file or xlsx file with images, and paths to the location  of the frame. 

    
   Uncomment out this section to get the frames directory and generate frames from the video. 
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
    cv2.destroyAllWindows()""" 
