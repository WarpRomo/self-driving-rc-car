import numpy;
import cv2
import pygame;
import json;

from os import listdir;
from os.path import isfile, join;

from car_module import CarControl;

car_max_speed = 0.3;

mouseX = 0;
mouseY = 0;
clicked = False;
just_clicked = False;

key_col = (255,0,0);
key_col_hover = (220,0,0);
key_col_pressed = (160,0,0);

key_pad_x = 70;
key_pad_y = 300;

key_pad_size = 80;
key_pad_padding = 10;

joy_stick_size = 200;
joy_stick_button_size = 60;

data_recorder_size = 50;

def main():

    CarManager = CarControl('http://20.1.1.70:5000', delay_check_rate=0.5);

    w_key = ((key_pad_x + key_pad_padding + key_pad_size, key_pad_y), (key_pad_size, key_pad_size));
    s_key = ((key_pad_x + key_pad_padding + key_pad_size, key_pad_y + key_pad_padding + key_pad_size), (key_pad_size, key_pad_size));

    a_key = ((key_pad_x, key_pad_y + key_pad_padding + key_pad_size), (key_pad_size, key_pad_size));
    d_key = ((key_pad_x + 2*key_pad_padding + 2*key_pad_size, key_pad_y + key_pad_padding + key_pad_size), (key_pad_size, key_pad_size));

    joy_stick = ((key_pad_x + 1.5*key_pad_size + key_pad_padding - 0.5 * joy_stick_size, key_pad_y + 2*key_pad_padding + 2*key_pad_size), (joy_stick_size, joy_stick_size));

    joy_stick_pos = (0,0);
    moving_joy_stick = False;

    data_recorder = ((key_pad_x + key_pad_size - data_recorder_size, key_pad_y + key_pad_size - data_recorder_size),(data_recorder_size, data_recorder_size));
    data_recording = False;
    prev_record = False;
    data_frames = [];

    img_size = (320,240);
    img_pos = (40,40);

    pygame.init();

    pygame.display.set_caption("RC Car Control");

    pygame.font.init();
    font = pygame.font.SysFont('Arial', 30);
    font_small = pygame.font.SysFont('Arial', 20);

    display = pygame.display.set_mode((400, 700))

    clock = pygame.time.Clock()

    running = True;

    goal_fps = 60

    try:

        global clicked;
        global just_clicked;
        global mouseX;
        global mouseY;

        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False;
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if clicked == False:
                        just_clicked = True;
                    clicked = True;
                if event.type == pygame.MOUSEBUTTONUP:
                    clicked = False;

            display.fill((30,30,30));

            mouseX = pygame.mouse.get_pos()[0];
            mouseY = pygame.mouse.get_pos()[1];

            dataArray = CarManager.carImage;

            if len(dataArray) != 0:
                dataArray = cv2.resize(dataArray, dsize=(img_size[0], img_size[1]), interpolation= cv2.INTER_AREA)

                camera_image = cv2.rotate(dataArray, cv2.ROTATE_90_COUNTERCLOCKWISE)

                surf = pygame.surfarray.make_surface(camera_image);

                #print((CarManager.carImageTurn, CarManager.carImageSpeed));

                display.blit(surf, img_pos);

            forw = draw_button(display, w_key, key_col, key_col_hover, key_col_pressed, ord("w"), "W", font, False);
            back = draw_button(display, s_key, key_col, key_col_hover, key_col_pressed, ord("s"), "S", font, False);
            left = draw_button(display, a_key, key_col, key_col_hover, key_col_pressed, ord("a"), "A", font, False);
            right = draw_button(display, d_key, key_col, key_col_hover, key_col_pressed, ord("d"), "D", font, False);

            record = draw_button(display, data_recorder, key_col, key_col_hover, key_col_pressed, ord("r"), "R", font_small);

            joy_stick_rectangle = pygame.Rect(joy_stick[0][0], joy_stick[0][1], joy_stick[1][0], joy_stick[1][1]);
            pygame.draw.rect(display, (30,30,30), joy_stick_rectangle);
            pygame.draw.rect(display, (0,0,0), joy_stick_rectangle, 10);


            joy_stick_center = (joy_stick[0][0] + joy_stick[1][0]/2, joy_stick[0][1] + joy_stick[1][1]/2);

            if not clicked:
                moving_joy_stick = False;
                joy_stick_pos = (0,0);

            if moving_joy_stick:
                dx = mouseX - joy_stick_center[0]
                dy = mouseY - joy_stick_center[1]

                max_d = joy_stick_size/2 - joy_stick_button_size/2;

                if abs(dy) > max_d:
                    dy = abs(dy)/dy * max_d

                if abs(dx) > max_d:
                    dx = abs(dx)/dx * max_d


                norm = (dx / max_d, (-dy / max_d) * car_max_speed);

                CarManager.turn(norm[0]);
                CarManager.speed(norm[1]);

                joy_stick_pos = (dx,dy);

            joy_stick_pos2 = ((joy_stick_center[0] + joy_stick_pos[0] - joy_stick_button_size/2, joy_stick_center[1] + joy_stick_pos[1] - joy_stick_button_size/2), (joy_stick_button_size, joy_stick_button_size));
            joy_stick_button = draw_button(display, joy_stick_pos2, key_col, key_col_hover, key_col_pressed, ord("j"), "J", font_small)

            if just_clicked and joy_stick_button:
                moving_joy_stick = True;



            save_frames = False;

            if record and record != prev_record:
                data_recording = not data_recording
                if not data_recording:
                    save_frames = True;


            prev_record = record;

            if data_recording:

                draw_text(display, (img_pos[0], img_pos[1]), "Recording " + str(len(data_frames)), font, (0,255,0), False);

                prev = [-1,-1,-1,-1];

                if len(data_frames) > 0: prev = data_frames[len(data_frames)-1];

                if prev[3] != CarManager.carImageFrame:
                    data_frames.append([CarManager.carImage.tolist(), CarManager.carImageTurn, CarManager.carImageSpeed, CarManager.carImageFrame]);

            if save_frames:
                files = listdir("./recordings");
                index = 0;

                for i in range(0, len(files)):
                    file_index = int(files[i].split(".")[0]);
                    if file_index >= index: index = file_index + 1;

                f = open("./recordings/" + str(index) + ".json", "w");
                f.write(json.dumps(data_frames))
                f.close();

                print("writing");

                data_frames = [];


            delayMS_text = font.render(str(int(CarManager.delayMS*1000))+"ms", False, (0,255,0));
            display.blit(delayMS_text, (img_pos[0], img_pos[1]-35));

            if not moving_joy_stick:
                turn = 0;
                speed = 0;

                if left: turn = -1;
                if right: turn = 1;

                if forw: speed = car_max_speed;
                if back: speed = -car_max_speed;

                CarManager.turn(turn);
                CarManager.speed(speed);

            pygame.display.flip();

            just_clicked = False;

            clock.tick(goal_fps);
    except KeyboardInterrupt:
        CarManager.terminate();
        print("Keyboard Interrupt");

def paste_image(l_img, s_img, x_offset, y_offset):
    l_img[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1]] = s_img

def draw_text(display, pos, text, font, col=(255,255,255), centered=True):
    text = font.render(text, False, col);
    center_pos = (pos[0], pos[1]);
    w,h = text.get_size();

    text_pos = (center_pos[0] - w/2, center_pos[1] - h/2);

    if not centered:
        text_pos = pos;

    display.blit(text, text_pos)

def draw_button(display, pos, col, hoverCol, pressedCol, shortcut_key, text, font, can_click=True):

    p1 = pos[0];
    p2 = pos[1];

    end_col = col;

    pressed = False;

    if p2[0]+p1[0] >= mouseX >= p1[0] and p2[1]+p1[1] >= mouseY >= p1[1]:

        end_col = hoverCol;

        if clicked and can_click:
            pressed = True;
            end_col = pressedCol;

    if shortcut_key != False:

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[shortcut_key]:
                pressed = True;
                end_col = pressedCol;

    rectangle = pygame.Rect(p1[0], p1[1], p2[0], p2[1]);

    pygame.draw.rect(display, end_col, rectangle);
    pygame.draw.rect(display, (0,0,0), rectangle, 10);

    draw_text(display, (p1[0] + p2[0]/2, p1[1] + p2[1]/2), text, font)

    return pressed;


if  __name__ == '__main__':
    main();
