import numpy;
import cv2
import pygame;
import json;

from configparser import ConfigParser #load IP address
config = ConfigParser()
config.read('config.ini')

from os import listdir;
from os.path import isfile, join;

from car_module import CarControl;

car_max_speed = 0.3;

mouseX = 0;
mouseY = 0;
clicked = False;
just_clicked = False;

move_key_col = (100,100,100);
move_key_pressed = (100,70,70);
key_col = (255,0,0);
key_col_hover = (220,0,0);
key_col_pressed = (160,0,0);

img_size = (320,240);
img_pos = (40,16);

key_pad_x = 90;
key_pad_y = 270;

key_pad_size = 70;
key_pad_padding = 7;

joy_stick_size = 180;
joy_stick_button_size = 50;

data_recorder_size = 50;

speed_slider_ticks = 20;
speed_slider_padding = 45;
speed_slider_width = 20;
speed_slider_but_height = 38;
speed_slider_but_width = 50;

def main():

    print(('http://' + config.get('main', 'ip')));

    CarManager = CarControl('http://' + config.get('main', 'ip'), delay_check_rate=0.5);

    w_key = ((key_pad_x + key_pad_padding + key_pad_size, key_pad_y), (key_pad_size, key_pad_size));
    s_key = ((key_pad_x + key_pad_padding + key_pad_size, key_pad_y + key_pad_padding + key_pad_size), (key_pad_size, key_pad_size));

    a_key = ((key_pad_x, key_pad_y + key_pad_padding + key_pad_size), (key_pad_size, key_pad_size));
    d_key = ((key_pad_x + 2*key_pad_padding + 2*key_pad_size, key_pad_y + key_pad_padding + key_pad_size), (key_pad_size, key_pad_size));

    joy_stick = ((key_pad_x + 1.5*key_pad_size + key_pad_padding - 0.5 * joy_stick_size - 1, key_pad_y + 2*key_pad_padding + 2*key_pad_size + 5), (joy_stick_size, joy_stick_size));

    joy_stick_pos = (0,0);
    moving_joy_stick = False;

    data_recorder = ((key_pad_x + key_pad_size - data_recorder_size, key_pad_y + key_pad_size - data_recorder_size),(data_recorder_size, data_recorder_size));
    data_recording = False;
    prev_record = False;
    data_frames = [];

    moving_speed_slider = False;

    pygame.init();

    pygame.display.set_caption("RC Car Control");

    pygame.font.init();
    font = pygame.font.SysFont('Arial', 30);
    font_small = pygame.font.SysFont('Arial', 20);

    display = pygame.display.set_mode((400, 630))

    clock = pygame.time.Clock()

    running = True;

    goal_fps = 60

    try:

        global clicked;
        global just_clicked;
        global mouseX;
        global mouseY;
        global car_max_speed;

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
                if event.type == pygame.MOUSEMOTION:
                    mouseX = event.pos[0];
                    mouseY = event.pos[1];

            display.fill((90,90,90));

            mouseX = pygame.mouse.get_pos()[0];
            mouseY = pygame.mouse.get_pos()[1];

            dataArray = CarManager.carImage;

            if len(dataArray) != 0:
                dataArray = cv2.resize(dataArray, dsize=(img_size[0], img_size[1]), interpolation= cv2.INTER_AREA)

                camera_image = cv2.rotate(dataArray, cv2.ROTATE_90_COUNTERCLOCKWISE)

                surf = pygame.surfarray.make_surface(camera_image);

                #print((CarManager.carImageTurn, CarManager.carImageSpeed));

                outline = pygame.Rect(img_pos[0], img_pos[1], img_size[0], img_size[1]);

                pygame.draw.rect(display, (0,0,0), outline.inflate(15,15), border_radius=10);

                display.blit(surf, img_pos);

            forw = draw_button(display, w_key, move_key_col, move_key_col, move_key_pressed, ord("w"), "W", font, can_click=False);
            back = draw_button(display, s_key, move_key_col, move_key_col, move_key_pressed, ord("s"), "S", font, can_click=False);
            left = draw_button(display, a_key, move_key_col, move_key_col, move_key_pressed, ord("a"), "A", font, can_click=False);
            right = draw_button(display, d_key, move_key_col, move_key_col, move_key_pressed, ord("d"), "D", font, can_click=False);

            record = draw_button(display, data_recorder, key_col, key_col_hover, key_col_pressed, 312, "", font_small, border_radius=10);

            joy_stick_rectangle = pygame.Rect(joy_stick[0][0], joy_stick[0][1], joy_stick[1][0], joy_stick[1][1]);

            pygame.draw.rect(display, (0,0,0), joy_stick_rectangle.inflate(15,15), border_radius=10);
            pygame.draw.rect(display, (70,70,70), joy_stick_rectangle, border_radius=10);
            pygame.draw.line(display, (140,140,140), (joy_stick[0][0] + joy_stick[1][0]/2, joy_stick[0][1]), (joy_stick[0][0] + joy_stick[1][0]/2, joy_stick[0][1] + joy_stick[1][1]), width=2 )
            pygame.draw.line(display, (140,140,140), (joy_stick[0][0], joy_stick[0][1] + joy_stick[1][1]/2), (joy_stick[0][0] + joy_stick[1][0], joy_stick[0][1] + joy_stick[1][1]/2), width=2 )



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
                    pygame.mouse.set_pos((dx + joy_stick_center[0], dy + joy_stick_center[1]))

                if abs(dx) > max_d:
                    dx = abs(dx)/dx * max_d
                    pygame.mouse.set_pos((dx + joy_stick_center[0], dy + joy_stick_center[1]))

                pygame.mouse.set_visible(False);


                norm = (dx / max_d, (-dy / max_d) * car_max_speed);

                CarManager.turn(norm[0]);
                CarManager.speed(norm[1]);

                joy_stick_pos = (dx,dy);
            else:
                pygame.mouse.set_visible(True);

            joy_stick_pos2 = ((joy_stick_center[0] + joy_stick_pos[0] - joy_stick_button_size/2, joy_stick_center[1] + joy_stick_pos[1] - joy_stick_button_size/2), (joy_stick_button_size, joy_stick_button_size));
            joy_stick_button = draw_button(display, joy_stick_pos2, key_col, key_col_hover, key_col_pressed, 3412, "", font_small, border_radius=10)

            if just_clicked and joy_stick_button:
                moving_joy_stick = True;

            pygame.draw.line(display, (0,0,0), (joy_stick[0][0] - speed_slider_padding, joy_stick[0][1]), (joy_stick[0][0] - speed_slider_padding, joy_stick[0][1] + joy_stick_size), 5)

            for i in range(0, speed_slider_ticks+1):

                tickY = joy_stick[0][1] + (i / speed_slider_ticks) * joy_stick_size;
                tickX = joy_stick[0][0] - speed_slider_width/2 - speed_slider_padding;
                pygame.draw.line(display, (0,0,0), (tickX, tickY), (tickX + speed_slider_width, tickY), 3);

            currentTick = round(car_max_speed / (1 / speed_slider_ticks));

            currentButY = joy_stick[0][1] + joy_stick_size - currentTick / 20 * joy_stick_size - speed_slider_but_height / 2;
            currentButX = joy_stick[0][0] - speed_slider_but_width/2 - speed_slider_padding;

            speed_slider_button = ((currentButX+1, currentButY), (speed_slider_but_width, speed_slider_but_height))

            speed_slider_clicked = draw_button(display, speed_slider_button, key_col, key_col_hover, key_col_pressed, 39201, "", font_small, border_radius=5);

            draw_text(display, (currentButX + 1 + speed_slider_but_width/2, currentButY+18), str(int(car_max_speed*100)), font_small)

            if just_clicked and speed_slider_clicked:
                moving_speed_slider = True;

            if not clicked:
                moving_speed_slider = False;

            if moving_speed_slider:
                car_max_speed = -int( ((mouseY - (joy_stick[0][1] + joy_stick_size)) / joy_stick_size) * speed_slider_ticks ) / speed_slider_ticks;

                if car_max_speed > 1: car_max_speed = 1;
                if car_max_speed < 0: car_max_speed = 0;

            save_frames = False;

            if (record and record != prev_record) and just_clicked:
                data_recording = not data_recording
                if not data_recording:
                    save_frames = True;


            prev_record = record;

            if data_recording:

                draw_text(display, (img_pos[0] + 5, img_pos[1] + 25), "Recording " + str(len(data_frames)) + "f", font_small, (0,255,0), False);

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


            delayMS_text = font_small.render(str(int(CarManager.delayMS*1000))+"ms", False, (0,255,0));
            display.blit(delayMS_text, (img_pos[0] + 5, img_pos[1] + 2));

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

            #clock.tick(goal_fps);
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

def draw_button(display, pos, col, hoverCol, pressedCol, shortcut_key, text, font,
border_radius=15,
outline=15,
can_click=True,
text_color=(255,255,255),
outline_color=(0,0,0)):

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

    pygame.draw.rect(display, outline_color, rectangle, border_radius=border_radius);
    pygame.draw.rect(display, end_col, rectangle.inflate(-outline, -outline), border_radius=border_radius);

    draw_text(display, (p1[0] + p2[0]/2, p1[1] + p2[1]/2), text, font, col=text_color)

    return pressed;


if  __name__ == '__main__':
    main();
