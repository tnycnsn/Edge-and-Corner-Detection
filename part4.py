import pyautogui
import time
import cv2
import numpy as np


def add_padding(matrix):
    new_matrix = np.zeros((matrix.shape[0]+2, matrix.shape[1]+2))
    new_matrix[1:-1, 1:-1] = matrix.copy()
    return new_matrix


def matrix_convolve(matrix, kernel):

    row_num, colm_num = matrix.shape
    kernel_size = kernel.shape[0]

    padded_mtx = matrix
    for i in range(int(kernel_size/2)):
        padded_mtx = add_padding(padded_mtx)    # pad matrix with 1 layer of  0's

    convolution = np.zeros((row_num, colm_num)) #result of the convolution stored in here
    reversed_kernel = kernel[::-1, ::-1]    #take time reversal of signal in both dimentions
    for r in range(row_num):
        for c in range(colm_num):
            convolution[r, c] = np.sum(np.multiply(padded_mtx[r:r+kernel_size, c:c+kernel_size], reversed_kernel))

    return convolution


def path_plan(edges, img_shape, last_move):

    seed_x = int(img_shape[0]/2)
    seed_y = int(img_shape[1]/2)

    edges[seed_x-70 : seed_x+5, seed_y-30 : seed_y+30] = 0  #erase characters edge to initialize

    moves = []
    stop = False
    while len(moves) < 3 and not stop:  #terminate after reaching 3 tiles /or more

        up = np.nonzero(edges[:seed_x, seed_y] == 255)[0][::-1]         #beam to the upward
        u = np.nonzero([earlier < later + 3 for earlier, later in zip(up, up[1:])])[0] #check if any 2 successive edge is too near -3 pixel- each other
        up = np.delete(up, u)       #get rid off one of the near edge pixel

        down = np.nonzero(edges[seed_x:, seed_y] == 255)[0] #+ seed_x    #beam to the downward
        d = np.nonzero([earlier > later - 3 for earlier, later in zip(down, down[1:])])[0] #check if any 2 successive edge is too near -3 pixel- each other
        down = np.delete(down, d)     #get rid off one of the near edge pixel

        right = np.nonzero(edges[seed_x, seed_y:] == 255)[0] #+ seed_y   #beam to the right
        r = np.nonzero([earlier > later - 3 for earlier, later in zip(right, right[1:])])[0]  #check if any 2 successive edge is too near -3 pixel- each other
        right = np.delete(right, r)    #get rid off one of the near edge pixel

        left = np.nonzero(edges[seed_x, :seed_y] == 255)[0][::-1]       #beam to the left
        l = np.nonzero([earlier < later + 3 for earlier, later in zip(left, left[1:])])[0] #check if any 2 successive edge is too near -3 pixel- each other
        left = np.delete(left, l)     #get rid off one of the near edge pixel

        if len(up) > 1 and last_move != 's':
            #MOVE TO THE UP
            for i in range(len(up)-1):
                moves.append('w')
            seed_x = int((up[len(up)-1] + up[len(up)-2]) / 2)   #update seed_x as mid point of last 2 intersecting edges
            #seed_y remains unchanged
            last_move = 'w'

        elif len(down) > 1 and last_move != 'w':
            #MOVE TO THE DOWN
            for i in range(len(down)-1):
                moves.append('s')
            seed_x = int((down[len(down)-1] + down[len(down)-2]) / 2)   #update seed_x as mid point of last 2 intersecting edges
            #seed_y remains unchanged
            last_move = 's'

        elif len(right) > 1 and last_move != 'a':
            #MOVE TO THE RIGHT
            for i in range(len(right)-1):
                moves.append('d')
            #seed_x remains unchanged
            seed_y = int((right[len(right)-1] + right[len(right)-2]) / 2)   #update seed_x as mid point of last 2 intersecting edges
            last_move = 'd'

        elif len(left) > 1 and last_move != 'd':
            #MOVE TO THE LEFT
            for i in range(len(left)-1):
                moves.append('a')
            #seed_x remains unchanged
            seed_y = int((left[len(left)-1] + left[len(left)-2]) / 2)   #update seed_x as mid point of last 2 intersecting edges
            last_move = 'a'

        else:
            stop = True

    return moves


gaussian_five = np.array([[1,  4,  7,  4, 1], \
                            [4, 16, 26, 16, 4], \
                            [7, 26, 41, 26, 7], \
                            [4, 16, 26, 16, 4], \
                            [1,  4,  7,  4, 1]])
gaussian_five = gaussian_five/np.sum(gaussian_five) #ensure that result will be still in range of [0, 255]



time.sleep(5)
#in this 5 seconds you should switch to game screen to transfer the simulated keyboard inputs to the game.

last_move = 'o' #just give an initial char not 'w', 'a', 's', 'd'
while True:

    myScreenshot = pyautogui.screenshot()
    #And example screenshot is obtained. We will work on screenshots like this for this homework

    shot = np.array(myScreenshot)[:,:,::-1]
    cropped = shot[240:-250, 620:-620, :]
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

    smooth = np.uint8(matrix_convolve(gray, gaussian_five))    #filter with Gauessian
    edge_img = cv2.Canny(gray, 200, 250)                        #Extract edge map

    move_list = path_plan(edge_img, edge_img.shape, 'o')
    print(move_list)
    if not move_list:   #list is empty
        break
    last_move = move_list[len(move_list)-1] #update last_move

    for char in move_list:
        pyautogui.keyDown('shift')
        pyautogui.keyDown(char)

        time.sleep(1.9)

        pyautogui.keyUp(char)
        pyautogui.keyUp('shift')
        #pyautogui.keyUp and pyautogui.keyDown functions are used to simulate holding a button.
        #For simple presses, pyautogui.press can be used.
