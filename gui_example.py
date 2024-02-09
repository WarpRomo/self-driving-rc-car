import numpy;
import cv2
import pygame;

from car_module import CarControl;

car_max_speed = 0.35;

mouseX = 0;
mouseY = 0;
clicked = False;

key_col = (255,0,0);
key_col_hover = (220,0,0);
key_col_pressed = (160,0,0);

key_pad_x = 70;
key_pad_y = 300;

key_pad_size = 80;
key_pad_padding = 10;

def main():

    CarManager = CarControl('http://20.1.1.70:5000', control_rate=0.1, image_rate=0.1, image_downscale=10);

    w_key = ((key_pad_x + key_pad_padding + key_pad_size, key_pad_y), (key_pad_size, key_pad_size));
    s_key = ((key_pad_x + key_pad_padding + key_pad_size, key_pad_y + key_pad_padding + key_pad_size), (key_pad_size, key_pad_size));

    a_key = ((key_pad_x, key_pad_y + key_pad_padding + key_pad_size), (key_pad_size, key_pad_size));
    d_key = ((key_pad_x + 2*key_pad_padding + 2*key_pad_size, key_pad_y + key_pad_padding + key_pad_size), (key_pad_size, key_pad_size));

    img_size = (320,240);
    img_pos = (40,40);

    pygame.init();

    pygame.display.set_caption("RC Car Control");

    pygame.font.init();
    font = pygame.font.SysFont('Arial', 30);

    display = pygame.display.set_mode((400, 520))

    clock = pygame.time.Clock()

    running = True;

    goal_fps = 60

    try:
        while running:

            display.fill((30,30,30));

            mouseX = pygame.mouse.get_pos()[0];
            mouseY = pygame.mouse.get_pos()[1];

            dataArray = CarManager.carImage;

            if len(dataArray) != 0:
                dataArray = cv2.resize(dataArray, dsize=(img_size[0], img_size[1]), interpolation= cv2.INTER_AREA)

                camera_image = cv2.rotate(dataArray, cv2.ROTATE_90_COUNTERCLOCKWISE)

                surf = pygame.surfarray.make_surface(camera_image);

                display.blit(surf, img_pos);

            forw = draw_button(display, w_key, key_col, key_col_hover, key_col_pressed, ord("w"), "W", font);
            back = draw_button(display, s_key, key_col, key_col_hover, key_col_pressed, ord("s"), "S", font);
            left = draw_button(display, a_key, key_col, key_col_hover, key_col_pressed, ord("a"), "A", font);
            right = draw_button(display, d_key, key_col, key_col_hover, key_col_pressed, ord("d"), "D", font);

            delayMS_text = font.render(CarManager.delayMS, False, (255,255,255));
            display.blit(delayMS_text, img_pos);


            turn = 0;
            speed = 0;

            if left: turn = -1;
            if right: turn = 1;

            if forw: speed = car_max_speed;
            if back: speed = -car_max_speed;

            CarManager.turn(turn);
            CarManager.speed(speed);

            pygame.display.flip();

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False;
                if event.type == pygame.MOUSEBUTTONDOWN:
                    clicked = True;
                if event.type == pygame.MOUSEBUTTONUP:
                    clicked = False;

            clock.tick(goal_fps);
    except KeyboardInterrupt:
        CarManager.terminate();
        print("Keyboard Interrupt");

def paste_image(l_img, s_img, x_offset, y_offset):
    l_img[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1]] = s_img

def draw_button(display, pos, col, hoverCol, pressedCol, shortcut_key, text, font):

    p1 = pos[0];
    p2 = pos[1];

    end_col = col;

    pressed = False;

    if p2[0]+p1[0] >= mouseX >= p1[0] and p2[1]+p1[1] >= mouseY >= p1[1]:

        end_col = hoverCol;

        if clicked:
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
    text = font.render(text, False, (255,255,255));

    center_pos = (pos[0][0]+pos[1][0]/2, pos[0][1] + pos[1][1]/2);

    w,h = text.get_size();

    display.blit(text, (center_pos[0] - w/2, center_pos[1] - h/2))

    return pressed;


if  __name__ == '__main__':
    main();
