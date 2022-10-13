# import aitek CNN
import cv2 as cv2
import numpy as np
from . import c4dSettings as sett
################################################################################################
# Yolo Functions
################################################################################################
def ResizeAndPad(image, inputSize):
    canH = image.shape[0]
    canW = image.shape[1]

    # Create new image canvas
    new_image_width = max(canW, canH)
    new_image_height = max(canW, canH)
    color = (0, 0, 0)
    frame = np.full((new_image_height, new_image_width, 3), color, dtype=np.uint8)
    x_center = (new_image_width - canW) // 2
    y_center = (new_image_height - canH) // 2

    frame[y_center:y_center + canH, x_center:x_center + canW] = image

    # Normalize
    frame = frame / 255.0
    # Resize
    frame = cv2.resize(frame, inputSize)

    return frame  # return padded and resized 640x640 image


## Bundle function of frame spatial specifications ##
def frameSpecs(frame, inputSize):
    canH = frame.shape[0]
    canW = frame.shape[1]

    scaleW = canW / max(canW, canH)
    scaleH = canH / max(canW, canH)
    padFactor = (abs(canW - canH) / 2) / max(canW, canH) * inputSize[0]
    return (canH, canW, scaleW, scaleH, padFactor)


def inputPreprocess(frame, inputSize):
    # convert to RGB
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # create letterbox image and resize 640x640 (as the examples in the mail)
    img = ResizeAndPad(image, inputSize)
    image = img
    # Reshape and type float16
    img = np.expand_dims(img.transpose(2, 0, 1), axis=0)
    img = img.astype(np.float16)
    return np.array(img)


## Convert raw output to list of (xmin, ymin, w, h) entries for bounding boxes ##
def outputPreprocess(result_0, mOutputRow, mOutputColumn, frame):
    # flattening the output [][][] -> []
    outputs = []
    (canH, canW, scaleW, scaleH, padFactor) = frameSpecs(frame)

    for i in range(mOutputRow):
        for j in range(mOutputColumn):
            outputs.append(result_0[0][i][j])

    # process the output and convert boxes to xmin, ymin, w, h
    boxes = []
    for i in range(mOutputRow):
        conf = outputs[i * mOutputColumn + 4]
        if conf > 0.25:
            # extract box coordinates and compensate the added padding
            if canW > canH:
                xc = (outputs[i * mOutputColumn]) / (640 * scaleW)
                yc = (outputs[i * mOutputColumn + 1] - padFactor) / (640 * scaleH)
            else:
                xc = (outputs[i * mOutputColumn] - padFactor) / (640 * scaleW)
                yc = (outputs[i * mOutputColumn + 1]) / (640 * scaleH)
            # convert boxes to xmin, ymin, w, h
            w = outputs[i * mOutputColumn + 2] / (640 * scaleW)
            h = outputs[i * mOutputColumn + 3] / (640 * scaleH)
            x = xc - w / 2
            y = yc - h / 2

            # this step is only needed when the model has multiple classes
            boxes.append([x, y, w, h, conf])
    return boxes


def bb_intersection_over_union(boxA, boxB):
    IOU = 0
    AW = boxA[2]
    AH = boxA[3]
    Bx = boxB[0] - boxA[0]
    By = boxB[1] - boxA[1]
    BW = Bx + boxB[2]
    BH = By + boxB[3]

    # X overlap Calc
    if Bx < 0 and BW > 0:
        ovlpX = min(BW, AW)
    elif Bx > 0 and Bx < AW:
        ovlpX = min(BW, AW) - Bx
    elif Bx == 0:
        ovlpX = min(AW, BW)
    else:
        ovlpX = 0

    # Y overlap Calc
    if By < 0 and BH > 0:
        ovlpY = min(BH, AH)
    elif By > 0 and By < AH:
        ovlpY = min(BH, AH) - Bx
    elif By == 0:
        ovlpY = min(AH, BH)
    else:
        ovlpY = 0
    # Calculate Intersection over Union
    upp = ovlpX * ovlpY
    dwnn = AW * AH + BW * BH - upp
    if dwnn == 0.0:
        IOU = 255
    else:
        IOU = upp / dwnn
    return IOU


def FilterBoxesNMS(sorted_Boxes, iou_threshold):
    sorted_Boxes = sorted_Boxes.tolist()
    bbox_list = []
    stSize = len(sorted_Boxes)

    while stSize - len(bbox_list) != 0:
        bbox_list = []
        stSize = len(sorted_Boxes)
        while len(sorted_Boxes) > 0:
            current_box = sorted_Boxes.pop(0)
            bbox_list.append(current_box)
            list(bbox_list)
            for box in sorted_Boxes:
                iou = bb_intersection_over_union(current_box, box)
                if iou > iou_threshold:
                    sorted_Boxes.remove(box)
        sorted_Boxes = bbox_list
    return bbox_list


def printBBoxes(rem_bbox, frame):
    (canH, canW, scaleW, scaleH, padFactor) = frameSpecs(frame)

    for i in range(0, rem_bbox.shape[0]):
        boxYX = (int((rem_bbox[i, 0]) * canW),
                 int((rem_bbox[i, 1]) * canH))
        boxYrXr = (int((rem_bbox[i, 0] + rem_bbox[i, 2]) * canW),
                   int((rem_bbox[i, 1] + rem_bbox[i, 3]) * canH))

        box_rect = cv2.rectangle(frame, boxYX, boxYrXr, (0, 0, 180), 3)
    return frame

def WriteC4DVideo(img_array):
    (canH, canW, scaleW, scaleH, padFactor) = frameSpecs(img_array[0])
    out = cv2.VideoWriter('project.avi', cv2.VideoWriter_fourcc(*'DIVX'), 15, (canH, canW))
    print('Writing .avi')
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()
    print('avi written')

# Print Boxes on frame
def PrintBBoxOnFrame(frame, rem_bbox, frm_count, img_array ):
    frame = printBBoxes(rem_bbox, frame)
    if sett.write_frames:
        cv2.imwrite('frame_' + str(frm_count) + '.jpg', frame)
    img_array.append(frame)
    frm_count += 1

    return (img_array, frm_count)
