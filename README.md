# comp467-Project5-MultiMedia
Reading Baselight, xytech, and video demo files and getting frames, pictures, and clips. Uploading to Frame.io. Pictures get insertinto xlsxfile, paths, folders, and other frames to fix goes to csv
    
   Uncomment out this section to get frames directory and generate frames from video. 
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
