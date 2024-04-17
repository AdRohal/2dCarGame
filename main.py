import tkinter as tk
from tkinter import messagebox
import random
from PIL import Image, ImageTk

# Constants
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 500
LANE_WIDTH = 130
LANE_COUNT = 3
CAR_WIDTH = 40
CAR_HEIGHT = 70
WHITE = "white"
RED = "red"


# Game class
class CarGame:
    def __init__(self, master):
        self.master = master
        self.master.title("2DCar Game")
        self.canvas = tk.Canvas(master, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="white")  # Change background to white
        self.canvas.pack()

        # Title
        self.title_label = tk.Label(master, text="2DCar", font=("Arial", 24), fg="red", bg="white")  # Set background to white
        self.title_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

        # Start button
        self.start_button = tk.Button(master, text="Start the game", font=("Arial", 14), command=self.start_game)
        self.start_button.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

        self.game_started = False  # Flag to track whether the game has started
        self.countdown_label = None
        self.countdown = 3

        # Load and resize road background image
        self.road_image = Image.open("img/Road.jpg").resize((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.road_photo = ImageTk.PhotoImage(self.road_image)

        # Load and resize car images
        self.player_car_image = Image.open("img/RedCar.png").resize((CAR_WIDTH, CAR_HEIGHT))
        self.player_car_photo = ImageTk.PhotoImage(self.player_car_image)
        self.other_car_image = Image.open("img/WhiteCar.png").resize((CAR_WIDTH, CAR_HEIGHT))
        self.other_car_photo = ImageTk.PhotoImage(self.other_car_image)

        # Player car
        self.player_car = None

        self.other_cars = []
        self.speed = 5
        self.score = 0

        # Game over elements
        self.game_over_label = None
        self.score_label = None
        self.restart_button = None
        self.return_button = None

    def start_game(self):
        if not self.game_started:
            self.game_started = True
            self.start_button.destroy()
            self.title_label.destroy()

            # Restore road background
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.road_photo)

            # Countdown
            self.countdown_label = tk.Label(self.master, text="", font=("Arial", 36), fg="black", bg="white")
            self.countdown_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            self.update_countdown()

    def update_countdown(self):
        if self.countdown > 0:
            self.countdown_label.config(text=str(self.countdown))
            self.countdown -= 1
            self.master.after(1000, self.update_countdown)
        else:
            self.countdown_label.config(text="Go!!!")
            self.master.after(1000, self.start_game_after_countdown)

    def start_game_after_countdown(self):
        self.countdown_label.destroy()
        # Create player car
        self.player_car = self.canvas.create_image(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT - CAR_HEIGHT - 20,
            anchor=tk.CENTER, image=self.player_car_photo
        )

        # Reset other cars list
        self.other_cars = []

        self.master.bind("<Left>", self.move_left)
        self.master.bind("<Right>", self.move_right)

        self.master.after(1000, self.spawn_other_car)
        self.update()
    def move_left(self, event):
        if self.canvas.coords(self.player_car)[0] > 0:
            new_x = self.canvas.coords(self.player_car)[0] - LANE_WIDTH
            if new_x >= 0:
                self.canvas.move(self.player_car, -LANE_WIDTH, 0)

    def move_right(self, event):
        if self.canvas.coords(self.player_car)[0] < WINDOW_WIDTH - CAR_WIDTH:
            new_x = self.canvas.coords(self.player_car)[0] + LANE_WIDTH
            if new_x <= WINDOW_WIDTH - CAR_WIDTH:
                self.canvas.move(self.player_car, LANE_WIDTH, 0)

    def spawn_other_car(self):
        occupied_lanes = []
        for car in self.other_cars:
            coords = self.canvas.coords(car)
            if coords:
                occupied_lanes.append(coords[0] // LANE_WIDTH)
        empty_lanes = [lane for lane in range(LANE_COUNT) if lane not in occupied_lanes]
        if empty_lanes:
            lane = random.choice(empty_lanes)
        else:
            lane = random.randint(0, LANE_COUNT - 1)
        other_car = self.canvas.create_image(
            lane * LANE_WIDTH + LANE_WIDTH // 2, -CAR_HEIGHT // 2,
            anchor=tk.CENTER, image=self.other_car_photo
        )
        self.other_cars.append(other_car)
        self.master.after(1000, self.spawn_other_car)

    def update(self):
        if self.game_started:
            player_coords = self.canvas.coords(self.player_car)
            player_left = player_coords[0]
            player_right = player_coords[0] + CAR_WIDTH
            player_top = player_coords[1]
            player_bottom = player_coords[1] + CAR_HEIGHT

            for other_car in self.other_cars:
                other_coords = self.canvas.coords(other_car)
                other_left = other_coords[0]
                other_right = other_coords[0] + CAR_WIDTH
                other_top = other_coords[1]
                other_bottom = other_coords[1] + CAR_HEIGHT

                # Check for collision
                if (player_left < other_right and player_right > other_left and
                        player_top < other_bottom and player_bottom > other_top):
                    self.game_over()
                    return

            for other_car in self.other_cars:
                self.canvas.move(other_car, 0, self.speed)
                if self.canvas.coords(other_car)[1] > WINDOW_HEIGHT:
                    self.canvas.delete(other_car)
                    self.other_cars.remove(other_car)
                    self.score += 1

            self.master.after(50, self.update)

    def game_over(self):
        self.game_started = False

        # Display "Game Over!!"
        self.game_over_label = tk.Label(self.master, text="Game Over!!", font=("Arial", 24), fg="red", bg="white")
        self.game_over_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

        # Display score
        self.score_label = tk.Label(self.master, text=f"Score: {self.score}", font=("Arial", 18), bg="white")
        self.score_label.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

        # Restart button
        self.restart_button = tk.Button(self.master, text="Restart", font=("Arial", 14), command=self.restart_game)
        self.restart_button.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        # Return to start page button
        self.return_button = tk.Button(self.master, text="Return to Start Page", font=("Arial", 14),
                                        command=self.return_to_start_page)
        self.return_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

    def restart_game(self):
        self.score = 0
        self.canvas.delete("all")  # Clear the canvas
        self.game_over_label.destroy()
        self.score_label.destroy()
        self.restart_button.destroy()
        self.return_button.destroy()
        self.start_game()  # Restart the game

    def return_to_start_page(self):
        self.canvas.delete("all")  # Clear the canvas
        self.score = 0
        self.game_started = False
        self.game_over_label.destroy()
        self.score_label.destroy()
        self.restart_button.destroy()
        self.return_button.destroy()
        self.start_button = tk.Button(self.master, text="Start the game", font=("Arial", 14), command=self.start_game)
        self.start_button.place(relx=0.5, rely=0.2, anchor=tk.CENTER)
        self.title_label = tk.Label(self.master, text="2DCar", font=("Arial", 24), fg="red", bg="white")
        self.title_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)


# Main function
def main():
    root = tk.Tk()
    game = CarGame(root)

    # Center the window
    window_width = WINDOW_WIDTH
    window_height = WINDOW_HEIGHT
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = (screen_width / 2) - (window_width / 2)
    y_coordinate = (screen_height / 2) - (window_height / 2)
    root.geometry(f"{window_width}x{window_height}+{int(x_coordinate)}+{int(y_coordinate)}")

    root.mainloop()


# Run the game
if __name__ == "__main__":
    main()
