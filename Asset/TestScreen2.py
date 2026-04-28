

# 可以在裡面測試不同項目
def test_screen2(self, events):
    # --- 1. Draw background. ---
    # Draw the background.
    self.DrawBackground()

    # --- 2. Draw player. ---
    self.DrawPlayer()

    # --- 3. Handles keyboard input (Player Movement). ---
    self.KeyBoardDetectionAndSetCamera()