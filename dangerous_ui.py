from tkinter import *
from tkinter.ttk import *
import time

# Number of characters to be written to save progress
WORDS_TO_SAFEPOINT = 100


# UI -------------------------------------------------------------------------------------------------------------------
class DangerousUI(Tk):
    def __init__(self, seconds):
        # Initialize Tk
        super().__init__()
        text_font = ("Calibri", 14, "normal")
        label_font = ("Segoe UI", 16, "normal")

        # Change Tk window title
        self.title("Dangerous Writing")
        # Tk window padding
        self.config(padx=10, pady=10)

        # Grid and column configuration to make them resizeable
        Grid.rowconfigure(self, 2, weight=1)
        Grid.columnconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 1, weight=1)

        # Main UI ------------------------------------------------------------------------------------------------------

        # Top label
        self.label_count = Label(text="Word count: 000/100", font=label_font)
        self.label_count.grid(column=0, row=0, sticky="W")
        self.label_text = Label(text="Time remaining: 00:10", font=label_font)
        self.label_text.grid(column=1, row=0, sticky="E")
        # Text field
        self.text = Text(self, width=100, height=20, wrap="word")
        self.text.grid(column=0, row=2, columnspan=2, sticky="NSEW")
        self.text.configure(font=text_font)
        self.text.focus_set()
        # progress bar
        self.seconds = seconds
        self.update_interval = 0.01
        self.progress_bar = Progressbar(self, orient=HORIZONTAL, length=100, mode="determinate")
        self.progress_bar.grid(column=0, row=1, pady=10, columnspan=2, sticky="NSEW")
        # Test button
        self.button = Button(self, text="Test", command=self.time_it)
        self.button.grid(column=0, row=3, pady=10, columnspan=2, sticky="NSEW")

        # Keypress detection -------------------------------------------------------------------------------------------

        # Works only when using lambda function with one parameter - e.g. "x", to pass self to time_it()
        self.text.bind("<KeyRelease>", lambda x: self.time_it())
        self.text.bind("<KeyPress>", lambda x: self.stop_countdown())

        # Variables ----------------------------------------------------------------------------------------------------

        self.run = True
        self.safe_point = None
        self.words_to_safepoint = WORDS_TO_SAFEPOINT

    # Timer ------------------------------------------------------------------------------------------------------------

    def time_it(self):
        # Progress bar increment step size 100% / time * update interval (time.sleep() value)
        # Doesn't work, with low update intervals, progress bar is filled slower than the time expires
        # step_size = 100 / self.seconds * self.update_interval
        # Check the number of characters
        self.check_safepoint()
        # Start countdown
        self.countdown()

    def check_safepoint(self):
        """Checks whether the safe point was reached. In case it was, creates new safe point in self.safe_point
        and sets the new value for self.words_to_safepoint."""
        num_of_words = self.count_words()

        if num_of_words == self.words_to_safepoint:
            print("Safepoint reached!")
            # Get last word's length
            word_length = self.last_word_length() + 1
            print(f"Word length: {word_length}")
            # Assign the index of the last character of the last full word to safepoint
            # index = end - number of characters of the last unfinished word
            self.safe_point = self.text.index(f"end-{word_length}c")
            # Setting the next safe_point
            self.words_to_safepoint += WORDS_TO_SAFEPOINT

        # Update label with character count
        self.update_label_count(num_of_words)

    def last_word_length(self):
        """Finds the last word and returns its length
        :rtype word_length: int"""
        all_words = self.text.get("1.0", "end").split()
        # Index of the last character of the last full word
        print(f"Last word: {all_words[-1]}")
        word_length = len(all_words[-1])

        return word_length

    def count_words(self):
        """Counts number of words in text box.
        :rtype num_of_words: int"""
        num_of_words = len(self.text.get("1.0", "end").split())
        return num_of_words

    def update_label_count(self, num_of_words):
        """Updates label with word count
        :type num_of_words: int"""
        self.label_count.config(text=f"Word count: {format(num_of_words, '03d')}/{format(self.words_to_safepoint, '03d')}")

    def delete_text(self):
        """Deletes text in text box from self.safe_point to the end."""
        # Only characters after the current safe_point will be deleted
        if self.safe_point:
            self.text.delete(self.safe_point, "end")
        else:
            self.text.delete("1.0", "end")
        # Update character count label
        self.update_label_count(self.count_words())

    def stop_countdown(self):
        """Stops countdown"""
        self.run = False

    def update_progressbar(self, progress):
        """Updates progress_bar values
        :type progress: float"""
        self.progress_bar["value"] = progress

    def countdown(self):
        """Main method, keeps track of time, updates labels and deletes text after time expiration."""
        # Set self.run back to True, so new countdown can start
        self.run = True
        start = time.time()
        end = start + self.seconds
        now = time.time()
        full_time = end - start

        # Stop the loop when time's up or when another countdown starts
        while now < end and self.run:
            time.sleep(self.update_interval)
            time_remaining = end - now
            # To make sure countdown doesn't go under 00:00
            if time_remaining >= 0:
                # Calculate remaining minutes and seconds
                minutes = int((time_remaining) / 60)
                seconds = int((time_remaining) % 60)
            # Update countdown label
            self.label_text.config(text=f"Time remaining: {format(minutes, '02d')}:{format(seconds, '02d')}")
            # Update progress bar
            # self.progress_bar["value"] += step_size
            progress = 100 - (time_remaining / full_time * 100)
            self.update_progressbar(progress)

            # Use self.update instead of update_idletasks(), otherwise window freezes
            self.update()
            now = time.time()
        # When times up (loop finished, but self.run is True)
        # -> loop hasn't been stopped by another KeyPress event
        # delete text from the last safe_point
        if self.run:
            print("Deleting")
            self.delete_text()
