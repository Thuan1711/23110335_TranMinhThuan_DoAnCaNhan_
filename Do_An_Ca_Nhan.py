import tkinter as tk
from tkinter import ttk  
from tkinter import messagebox, simpledialog
import numpy as np
from collections import deque
import time
import heapq
import copy
import random
import math 

IDA_DEBUG_PRINT = False

class Puzzle8App:
    def __init__(self, root):
        self.root = root
        self.root.title("tranminhthuan_23110335_AI_Project") 

        self.default_start_state = np.array([[2, 6, 5], [0, 8, 7], [4, 3, 1]])
        self.goal_state = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
        self.stop_flag = False

        self.animation_speed = 0.5

        # Status bar setup
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)

        # --- Initial Setup ---
        self.is_belief_mode = False
        self.initial_belief_states = []

        # --- Heuristic Selection ---
        self.heuristic_var = tk.StringVar(value="Manhattan") 

        # Mặc định bắt đầu ở chế độ chuẩn
        self.start_state = self.get_user_input_state()


        self.create_ui()
        self.update_status("Sẵn sàng.")


    def update_status(self, message):
        try:
            if self.root.winfo_exists():
                self.status_var.set(message)
                self.root.update_idletasks()
        except tk.TclError as e:
            print(f"Ignoring TclError during status update: {e}")

    def ask_single_initial_state(self, prompt_message="Nhập trạng thái ban đầu"):
        new_state = []
        numbers_seen_so_far = set() 
        current_state_numbers = set() 

        title = "Nhập trạng thái"
        if hasattr(self, 'current_belief_input_seen_total'):
            numbers_seen_so_far = self.current_belief_input_seen_total
            title = f"Nhập trạng thái vật lý #{getattr(self, 'current_belief_state_count', 1)}"

        for i in range(3):
            while True:
                all_seen_for_prompt = sorted(list(numbers_seen_so_far.union(current_state_numbers)))
                entered_nums_str = f"Các số đã nhập (tổng thể): {all_seen_for_prompt}" if all_seen_for_prompt else ""

                row_str = simpledialog.askstring(title,
                                                 f"{prompt_message}\nNhập 3 số cho hàng {i+1} (0-8, cách nhau bởi dấu cách):\n"
                                                 f"{entered_nums_str}", parent=self.root)
                if row_str is None:
                    if hasattr(self, 'current_belief_input_seen_total'): del self.current_belief_input_seen_total
                    if hasattr(self, 'current_belief_state_count'): del self.current_belief_state_count
                    return None
                try:
                    row = list(map(int, row_str.split()))
                    if len(row) != 3: raise ValueError("Phải nhập đúng 3 số.")
                    if any(x < 0 or x > 8 for x in row): raise ValueError("Các số phải nằm trong khoảng từ 0 đến 8.")

                    temp_row_nums = set()
                    for num in row:
                        if num in numbers_seen_so_far: raise ValueError(f"Số {num} đã được dùng trong trạng thái belief trước đó.")
                        if num in current_state_numbers: raise ValueError(f"Số {num} đã được nhập cho trạng thái hiện tại này.")
                        if num in temp_row_nums: raise ValueError(f"Số {num} bị lặp lại trong hàng này.")
                        temp_row_nums.add(num)

                    new_state.append(row)
                    current_state_numbers.update(temp_row_nums) # Add to numbers for current 3x3 grid
                    break
                except ValueError as e:
                    messagebox.showerror("Lỗi nhập liệu", f"Dữ liệu không hợp lệ: {e}\nVui lòng nhập lại.", parent=self.root)

        flat_list = [item for sublist in new_state for item in sublist]
        final_seen_this_state = set(flat_list)
        if len(flat_list) != 9 or final_seen_this_state != set(range(9)):
             messagebox.showerror("Lỗi", "Trạng thái cuối cùng không hợp lệ (thiếu số hoặc trùng số). Vui lòng thử lại.", parent=self.root)
             if hasattr(self, 'current_belief_input_seen_total'): del self.current_belief_input_seen_total
             if hasattr(self, 'current_belief_state_count'): del self.current_belief_state_count
             return None
        if hasattr(self, 'current_belief_input_seen_total'):
            self.current_belief_input_seen_total.update(final_seen_this_state)

        return np.array(new_state)

    def get_user_input_belief_state(self):
        belief_states_list = []
        state_count = 1
        belief_state_tuples = set()
        self.current_belief_input_seen_total = set() 

        while True:
            self.current_belief_state_count = state_count
            new_state_np = self.ask_single_initial_state("") 

            if new_state_np is None: # User cancelled
                if not belief_states_list:
                    messagebox.showinfo("Thông báo", "Đã hủy nhập Belief State.", parent=self.root)
                    if hasattr(self, 'current_belief_input_seen_total'): del self.current_belief_input_seen_total
                    if hasattr(self, 'current_belief_state_count'): del self.current_belief_state_count
                    return None
                else:
                    break # Finished adding states

            if not self.is_solvable(new_state_np):
                 messagebox.showerror("Lỗi", "Trạng thái này không thể giải được. Vui lòng nhập trạng thái khác.", parent=self.root)
                 # Remove the numbers of this invalid state from the total seen set so they can be reused.
                 for r in new_state_np:
                     for val in r:
                         self.current_belief_input_seen_total.discard(val)
                 continue

            new_state_tuple = self.state_to_tuple(new_state_np)
            if new_state_tuple in belief_state_tuples:
                messagebox.showwarning("Trùng lặp", "Trạng thái này đã được nhập.", parent=self.root)
                for r in new_state_np: # Also remove from total if it was a duplicate that was 'validly' entered
                     for val in r:
                         self.current_belief_input_seen_total.discard(val)
            else:
                belief_states_list.append(new_state_np)
                belief_state_tuples.add(new_state_tuple)
                state_count += 1
                # Numbers for this valid state are now part of current_belief_input_seen_total

            if new_state_np is not None:
                 add_more = messagebox.askyesno("Thêm trạng thái?", "Nhập thêm trạng thái vật lý ban đầu khác?", parent=self.root)
                 if not add_more:
                     break
        # Clean up helper attributes
        if hasattr(self, 'current_belief_input_seen_total'): del self.current_belief_input_seen_total
        if hasattr(self, 'current_belief_state_count'): del self.current_belief_state_count

        if belief_states_list:
            self.update_status(f"Đã nhập {len(belief_states_list)} trạng thái cho Belief State.")
            return belief_states_list
        else:
            return None

    def switch_to_belief_mode(self):
        self.stop_puzzle()
        self.update_status("Chuyển sang chế độ Belief State...")
        # Clear any previous belief state input tracking
        if hasattr(self, 'current_belief_input_seen_total'): del self.current_belief_input_seen_total
        if hasattr(self, 'current_belief_state_count'): del self.current_belief_state_count

        belief_states = self.get_user_input_belief_state()
        if belief_states:
            self.is_belief_mode = True
            self.initial_belief_states = belief_states
            self.start_state = self.initial_belief_states[0].copy()
            self.update_grid(self.start_grid, self.start_state)
            self.clear_solution_path_display()
            self.algo_var.set("ConformantBFS")
            self.update_status(f"Chế độ Belief State hoạt động ({len(self.initial_belief_states)} trạng thái). Chọn ConformantBFS và Run.")
        else:
            self.is_belief_mode = False
            self.initial_belief_states = []
            self.update_status("Hủy Belief Mode hoặc không có trạng thái. Quay lại chế độ chuẩn.")


    def switch_to_standard_mode(self):
         self.stop_puzzle()
         self.update_status("Chuyển sang chế độ chuẩn...")
         self.is_belief_mode = False
         self.initial_belief_states = []
         # Ensure no belief input helper attributes linger
         if hasattr(self, 'current_belief_input_seen_total'): del self.current_belief_input_seen_total
         if hasattr(self, 'current_belief_state_count'): del self.current_belief_state_count

         # self.start_state = self.get_user_input_state() # Optionally re-input
         self.update_grid(self.start_grid, self.start_state)
         self.clear_solution_path_display()
         if self.algo_var.get() == "ConformantBFS":
              self.algo_var.set("BFS")
         self.update_status("Chế độ chuẩn hoạt động. Chọn thuật toán và Run.")


    def get_user_input_state(self):
        # Clear any belief state input tracking attributes if they exist
        if hasattr(self, 'current_belief_input_seen_total'): del self.current_belief_input_seen_total
        if hasattr(self, 'current_belief_state_count'): del self.current_belief_state_count

        try: has_status_var = hasattr(self, 'status_var')
        except Exception: has_status_var = False # Should not happen if init is correct

        use_default = messagebox.askyesno("Xác nhận trạng thái ban đầu", "Bắt đầu với chế độ chuẩn.\nBạn có muốn sử dụng trạng thái mặc định:\n[[2, 6, 5], [0, 8, 7], [4, 3, 1]] không?", parent=self.root if self.root.winfo_exists() else None)

        if use_default:
            state = self.default_start_state.copy()
            if has_status_var: self.update_status("Đã chọn trạng thái mặc định.")
            return state
        else:
            if has_status_var: self.update_status("Đang chờ nhập trạng thái thủ công...")
            while True:
                state = self.ask_single_initial_state("Nhập trạng thái ban đầu (chế độ chuẩn)")
                if state is None:
                    messagebox.showinfo("Thông báo", "Đã hủy nhập. Sử dụng trạng thái mặc định.", parent=self.root)
                    if has_status_var: self.update_status("Nhập liệu bị hủy. Sử dụng trạng thái mặc định.")
                    return self.default_start_state.copy()
                if self.is_solvable(state):
                    if has_status_var: self.update_status("Đã nhập trạng thái thủ công hợp lệ.")
                    return state
                else:
                    messagebox.showerror("Lỗi", "Trạng thái nhập vào không thể giải được. Vui lòng nhập lại.", parent=self.root)

    def state_to_tuple(self, state_np):
        if not isinstance(state_np, np.ndarray) or state_np.shape != (3, 3):
            # print(f"Warning: state_to_tuple received invalid state: {state_np}")
            return None
        return tuple(map(tuple, state_np))

    def apply_move(self, current_state_np, move_delta):
        try:
            zero_pos_list = np.argwhere(current_state_np == 0)
            if not zero_pos_list.size > 0: return None
            zero_pos = zero_pos_list[0] # e.g. array([1,0])
            # Ensure move_delta is a NumPy array for element-wise addition
            target_pos = zero_pos + np.array(move_delta)

            if 0 <= target_pos[0] < 3 and 0 <= target_pos[1] < 3:
                new_state = current_state_np.copy()
                # Swap
                new_state[zero_pos[0], zero_pos[1]], new_state[target_pos[0], target_pos[1]] = \
                    new_state[target_pos[0], target_pos[1]], new_state[zero_pos[0], zero_pos[1]]
                return new_state
            else:
                return None # Move is out of bounds
        except Exception as e:
            # print(f"Error in apply_move: {e}")
            return None


    def is_solvable(self, state):
        inversion_count = 0
        flat_state = state.flatten()
        puzzle_list = [i for i in flat_state if i != 0] # Exclude the blank tile
        for i in range(len(puzzle_list)):
            for j in range(i + 1, len(puzzle_list)):
                if puzzle_list[i] > puzzle_list[j]:
                    inversion_count += 1
        
        return inversion_count % 2 == 0

    def reinput_state(self):
        self.stop_puzzle()
        if self.is_belief_mode:
            self.update_status("Yêu cầu nhập lại Belief State...")
            self.switch_to_belief_mode()
        else:
            self.update_status("Yêu cầu nhập lại trạng thái chuẩn...")
            new_state_candidate = self.get_user_input_state()
            if new_state_candidate is not None: 
                self.start_state = new_state_candidate 
                self.update_grid(self.start_grid, self.start_state)
                self.clear_solution_path_display()
                self.update_status("Đã cập nhật trạng thái ban đầu (chuẩn).")


    def reset_puzzle(self):
        self.stop_puzzle()
        # If in belief mode, start_state is the first belief. Otherwise, it's the standard start_state
        self.update_grid(self.start_grid, self.start_state)
        self.clear_solution_path_display()
        mode_text = "Belief" if self.is_belief_mode else "Chuẩn"
        self.update_status(f"Giao diện đã được đặt lại về trạng thái ban đầu (Chế độ: {mode_text}).")


    def stop_puzzle(self):
        if not self.stop_flag:
            self.stop_flag = True
            self.update_status("Đã yêu cầu dừng...")

    
    def get_selected_heuristic(self, state):
        
        state_np = np.array(state)
        if state_np.shape != (3,3): 
            return float('inf')

        heuristic_name = self.heuristic_var.get()
        if heuristic_name == "Manhattan":
            return self.heuristic_manhattan(state_np)
        elif heuristic_name == "TilesOutOfPlace":
            return self.heuristic_tiles_out_of_place(state_np)
        else: 
            return self.heuristic_manhattan(state_np)

    def heuristic_manhattan(self, state_np): # Expects np.array
        try:
            # state_np is already an argument
            goal_positions = {val: idx for idx, val in np.ndenumerate(self.goal_state)}
            distance = 0
            for r in range(3):
                for c in range(3):
                    val = state_np[r, c]
                    if val != 0: # Don't count the blank tile
                        if val in goal_positions:
                            goal_r, goal_c = goal_positions[val]
                            distance += abs(r - goal_r) + abs(c - goal_c)
                        else:
                            return float('inf') # Invalid tile
            return distance
        except Exception as e:
            # print(f"Error in heuristic_manhattan: {e}")
            return float('inf')

    def heuristic_tiles_out_of_place(self, state_np): 
        try:
            misplaced = 0
            for r in range(3):
                for c in range(3):
                    current_val = state_np[r, c]
                    goal_val = self.goal_state[r, c] # Assumes self.goal_state is also np.array
                    if current_val != 0 and current_val != goal_val:
                        misplaced += 1
            return misplaced
        except Exception as e:
            return float('inf')

    # --- UI Creation ---
    def create_ui(self):
        top_main_frame = tk.Frame(self.root)
        top_main_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

        start_frame = tk.Frame(top_main_frame)
        start_frame.pack(side=tk.LEFT, expand=True, padx=10)
        tk.Label(start_frame, text="Trạng thái ban đầu / Hiện tại", font=("Arial", 12)).pack()
        self.start_grid_frame = tk.Frame(start_frame, bd=2, relief=tk.GROOVE)
        self.start_grid_frame.pack(pady=5)
        self.start_grid = self.create_grid(self.start_grid_frame, self.start_state, font_size=16)

        goal_frame = tk.Frame(top_main_frame)
        goal_frame.pack(side=tk.RIGHT, expand=True, padx=10)
        tk.Label(goal_frame, text="Trạng thái đích", font=("Arial", 12)).pack()
        self.goal_grid_frame = tk.Frame(goal_frame, bd=2, relief=tk.GROOVE)
        self.goal_grid_frame.pack(pady=5)
        self.goal_grid = self.create_grid(self.goal_grid_frame, self.goal_state, font_size=16)

        controls_container = tk.Frame(self.root)
        controls_container.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        left_controls_frame = tk.Frame(controls_container)
        left_controls_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True, padx=(0, 5))

        right_controls_frame = tk.Frame(controls_container)
        right_controls_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))

        self.create_buttons_and_heuristics(left_controls_frame)
        self.create_mode_buttons(right_controls_frame)
        self.create_speed_buttons(right_controls_frame)

        solution_frame = tk.LabelFrame(self.root, text="Các bước giải", padx=5, pady=5)
        solution_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.solution_canvas = tk.Canvas(solution_frame, borderwidth=0)
        self.solution_inner_frame = ttk.Frame(self.solution_canvas)
        self.solution_scrollbar = ttk.Scrollbar(solution_frame, orient="vertical", command=self.solution_canvas.yview)
        self.solution_canvas.configure(yscrollcommand=self.solution_scrollbar.set)
        self.solution_scrollbar.pack(side="right", fill="y")
        self.solution_canvas.pack(side="left", fill="both", expand=True)
        self.solution_canvas_window = self.solution_canvas.create_window((4,4), window=self.solution_inner_frame, anchor="nw")
        self.solution_inner_frame.bind("<Configure>", self.on_solution_frame_configure)
        self.solution_canvas.bind('<Configure>', self.on_solution_canvas_configure)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)


    def on_solution_frame_configure(self, event=None):
        self.solution_canvas.configure(scrollregion=self.solution_canvas.bbox("all"))

    def on_solution_canvas_configure(self, event=None):
         if not event: return
         canvas_width = event.width
         if self.solution_canvas.winfo_exists() and self.solution_canvas_window is not None:
             try:
                 self.solution_canvas.itemconfig(self.solution_canvas_window, width=max(0, canvas_width - 8))
             except tk.TclError:
                 pass

    def display_solution_path(self, path):
        self.clear_solution_path_display()
        if not isinstance(path, list):
             self.update_status("Lỗi hiển thị đường đi: Dữ liệu không hợp lệ.")
             return

        try:
             current_display_state = self.start_state.copy()
             
             if not path or not np.array_equal(np.array(path[0]), self.start_state):
                 
                  full_display_sequence = [self.start_state.tolist()] + path
             else: # Path already includes start state
                  full_display_sequence = path


             for i, state_data in enumerate(full_display_sequence):
                 state_np = np.array(state_data) 
                 if not isinstance(state_np, np.ndarray) or state_np.shape != (3, 3) :
                     
                     continue

                 step_frame = ttk.Frame(self.solution_inner_frame, padding=5)
                 step_frame.pack(side=tk.TOP, fill=tk.X, pady=2)
                 step_label = "B.đầu" if i == 0 else f"Bước {i}"
                 tk.Label(step_frame, text=f"{step_label}:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
                 grid_frame = tk.Frame(step_frame, bd=1, relief=tk.SOLID)
                 grid_frame.pack(side=tk.LEFT)
                 self.create_grid(grid_frame, state_np, font_size=9, cell_width=2, cell_height=1)

             self.solution_inner_frame.update_idletasks()
             self.solution_canvas.configure(scrollregion=self.solution_canvas.bbox("all"))
        except Exception as e:
             # print(f"ERROR during display_solution_path: {e}")
             import traceback
             traceback.print_exc()
             self.update_status(f"Lỗi hiển thị đường đi: {e}")


    def clear_solution_path_display(self):
         for widget in self.solution_inner_frame.winfo_children():
             widget.destroy()
         self.solution_canvas.configure(scrollregion=self.solution_canvas.bbox("all"))
         self.solution_canvas.yview_moveto(0)


    def create_grid(self, parent_frame, state, font_size=16, cell_width=4, cell_height=2):
        grid = []
        state_np = np.array(state) # Ensure it's a NumPy array
        if state_np.shape != (3,3):
             tk.Label(parent_frame, text="ERR", width=cell_width*3, height=cell_height*3, bg="red", fg="white").grid(row=0, column=0, rowspan=3, columnspan=3)
             return None

        for i in range(3):
            row_list = []
            for j in range(3):
                try:
                    val = state_np[i, j]
                    text = str(val) if val != 0 else ""
                    bg_color = "lightgrey" if val != 0 else "white"
                    cell = tk.Label(parent_frame, text=text, width=cell_width, height=cell_height,
                                    font=("Arial", font_size, "bold"), relief="solid", borderwidth=1, bg=bg_color)
                    cell.grid(row=i, column=j, padx=1, pady=1, sticky="nsew")
                    parent_frame.grid_rowconfigure(i, weight=1)
                    parent_frame.grid_columnconfigure(j, weight=1)
                    row_list.append(cell)
                except IndexError:
                     tk.Label(parent_frame, text="X", width=cell_width, height=cell_height, bg="red", fg="white").grid(row=i, column=j, padx=1, pady=1, sticky="nsew")
                except tk.TclError:
                     return None
            grid.append(row_list)
        return grid

    def create_buttons_and_heuristics(self, parent_frame):
        algo_frame = tk.LabelFrame(parent_frame, text="Chọn thuật toán", padx=5, pady=5)
        algo_frame.pack(side=tk.TOP, fill=tk.X, pady=(0,5))

        self.algo_var = tk.StringVar(value="BFS")
        algorithms = ["BFS", "DFS", "UCS", "IDDFS",
                      "Greedy", "A*", "IdA*",
                      "Hill", "Stp_Hill", "StochasticHill", "SimAnneal", "BeamSearch",
                      "AndOrSearch", "GeneticAlg", "ConformantBFS",
                      "Backtracking", "ForwardChecking", "QLearning"] # Added new ones
        max_cols_algo = 4 # Adjusted for more algorithms
        for i, algo in enumerate(algorithms):
            r, c = divmod(i, max_cols_algo)
            rb = ttk.Radiobutton(algo_frame, text=algo, variable=self.algo_var, value=algo,
                                 command=self.on_algo_select)
            rb.grid(row=r, column=c, padx=3, pady=1, sticky='w')

        heuristic_frame = tk.LabelFrame(parent_frame, text="Chọn Heuristic (cho thuật toán có thông tin)", padx=5, pady=5)
        heuristic_frame.pack(side=tk.TOP, fill=tk.X, pady=(0,5))

        heuristics = ["Manhattan", "TilesOutOfPlace"]
        for i, h_name in enumerate(heuristics):
            rb_h = ttk.Radiobutton(heuristic_frame, text=h_name, variable=self.heuristic_var, value=h_name)
            # Pack horizontally
            rb_h.pack(side=tk.LEFT, padx=5, pady=1)


        action_frame = tk.Frame(parent_frame)
        action_frame.pack(side=tk.TOP, pady=5)
        self.run_button = tk.Button(action_frame, text="Run", command=self.solve_puzzle, bg="#4CAF50", fg="white", width=9, font=("Arial", 10, "bold"))
        self.run_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(action_frame, text="Stop", command=self.stop_puzzle, bg="#f44336", fg="white", width=9, font=("Arial", 10, "bold"), state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Reset UI", command=self.reset_puzzle, bg="#ff9800", fg="white", width=9, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Nhập Lại", command=self.reinput_state, bg="#2196F3", fg="white", width=9, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)


    def on_algo_select(self):
        selected_algo = self.algo_var.get()
        is_informed = selected_algo in ["Greedy", "A*", "IdA*", "Hill", "Stp_Hill",
                                       "StochasticHill", "SimAnneal", "BeamSearch", "GeneticAlg",
                                       "Backtracking", "ForwardChecking"] 
                                                                    
        is_q_learning = selected_algo == "QLearning"

        
        for child in self.root.winfo_children(): # Find the heuristic frame
            if isinstance(child, tk.Frame): # The controls_container
                for l_child in child.winfo_children(): # left_controls_frame
                    if isinstance(l_child, tk.Frame):
                        for h_frame_candidate in l_child.winfo_children():
                            if isinstance(h_frame_candidate, tk.LabelFrame) and "Heuristic" in h_frame_candidate.cget("text"):
                                for rb_h in h_frame_candidate.winfo_children():
                                    if isinstance(rb_h, ttk.Radiobutton):
                                        rb_h.config(state=tk.NORMAL if is_informed or is_q_learning else tk.DISABLED)
                                break
                        break


        if selected_algo == "ConformantBFS":
            if not self.is_belief_mode:
                 self.switch_to_belief_mode()
        elif self.is_belief_mode and selected_algo != "ConformantBFS":
             
             if selected_algo not in ["QLearning"]: 
                self.switch_to_standard_mode()
        


    def create_mode_buttons(self, parent_frame):
        mode_frame = tk.LabelFrame(parent_frame, text="Chế độ", padx=5, pady=5)
        mode_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        btn_std = tk.Button(mode_frame, text="Chuẩn", width=10, command=self.switch_to_standard_mode, bg="#03A9F4", fg="white", font=("Arial", 9, "bold"))
        btn_std.pack(side=tk.LEFT, padx=3, pady=3)
        btn_belief = tk.Button(mode_frame, text="Belief State", width=10, command=self.switch_to_belief_mode, bg="#8BC34A", fg="white", font=("Arial", 9, "bold"))
        btn_belief.pack(side=tk.LEFT, padx=3, pady=3)

    def create_speed_buttons(self, parent_frame):
        speed_frame = tk.LabelFrame(parent_frame, text="Tốc độ hoạt ảnh", padx=5, pady=5)
        speed_frame.pack(side=tk.TOP, fill=tk.X)
        btn_frame = tk.Frame(speed_frame)
        btn_frame.pack()
        colors = {"Nhanh": "#4CAF50", "Trung": "#FFC107", "Chậm": "#F44336"}
        speeds = ["Nhanh", "Trung", "Chậm"]
        for speed in speeds:
            btn = tk.Button(btn_frame, text=speed, width=8, command=lambda s=speed: self.set_animation_speed(s), bg=colors[speed], fg="white", font=("Arial", 9, "bold"))
            btn.pack(side=tk.LEFT, padx=3, pady=3)

    def set_animation_speed(self, speed_name):
        if speed_name == "Nhanh": self.animation_speed = 0.1
        elif speed_name == "Trung": self.animation_speed = 0.5
        elif speed_name == "Chậm": self.animation_speed = 1.0
        self.update_status(f"Đã đặt tốc độ hoạt ảnh: {speed_name} ({self.animation_speed}s/bước)")

    def set_button_states(self, is_running):
        run_state = tk.DISABLED if is_running else tk.NORMAL
        stop_state = tk.NORMAL if is_running else tk.DISABLED
        other_state = tk.DISABLED if is_running else tk.NORMAL

        run_bg = 'grey' if is_running else '#4CAF50'
        stop_bg = '#f44336' if is_running else 'grey'
        # Storing references to buttons/frames would be cleaner than searching
        try:
            if hasattr(self, 'run_button') and self.run_button.winfo_exists(): self.run_button.config(state=run_state, bg=run_bg)
            if hasattr(self, 'stop_button') and self.stop_button.winfo_exists(): self.stop_button.config(state=stop_state, bg=stop_bg)

            

            
            widget_types_to_disable = (ttk.Radiobutton, tk.Button)
            frames_to_scan = []
            
            for child in self.root.winfo_children():
                if isinstance(child, tk.Frame): # controls_container
                    for l_child in child.winfo_children(): 
                        if isinstance(l_child, tk.Frame):
                            frames_to_scan.append(l_child) 

            for frame_to_scan in frames_to_scan:
                for sub_frame in frame_to_scan.winfo_children(): 
                    if isinstance(sub_frame, (tk.Frame, tk.LabelFrame)):
                        for widget in sub_frame.winfo_children():
                            if isinstance(widget, widget_types_to_disable):
                                if widget not in [getattr(self, 'run_button', None), getattr(self, 'stop_button', None)]:
                                    try: widget.config(state=other_state)
                                    except tk.TclError: pass
            self.root.update_idletasks()
        except tk.TclError as e:
             print(f"Warning: Could not configure buttons, window likely closing. Error: {e}")
        except Exception as e_gen:
             print(f"General error in set_button_states: {e_gen}")


    # --- Conformant BFS Solve ---
    def conformant_bfs_solve(self, max_nodes=50000):
        if not self.is_belief_mode or not self.initial_belief_states:
            messagebox.showerror("Lỗi", "Chưa ở chế độ Belief State hoặc chưa nhập trạng thái.", parent=self.root)
            return None, 0
        goal_tuple = self.state_to_tuple(self.goal_state)
        if goal_tuple is None:
             messagebox.showerror("Lỗi", "Trạng thái đích không hợp lệ.", parent=self.root)
             return None, 0

        initial_belief_tuples = set()
        for state_np in self.initial_belief_states:
            state_tuple = self.state_to_tuple(state_np)
            if state_tuple: initial_belief_tuples.add(state_tuple)
        if not initial_belief_tuples:
             messagebox.showerror("Lỗi", "Không có trạng thái ban đầu hợp lệ trong Belief State.", parent=self.root)
             return None, 0

        initial_belief_frozenset = frozenset(initial_belief_tuples)
        is_initial_goal = all(st == goal_tuple for st in initial_belief_frozenset)
        if is_initial_goal:
            self.update_status("ConformantBFS: Belief State ban đầu đã là đích.")
            return [], 0 # Path is empty as it's already goal

        queue = deque([(initial_belief_frozenset, [])]) # path here is sequence of moves (deltas)
        visited_belief_states = {initial_belief_frozenset}
        nodes_expanded = 0
        moves_deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)] # U, D, L, R (as np array diffs)

        while queue:
            if self.stop_flag: break
            if nodes_expanded >= max_nodes:
                 self.update_status(f"ConformantBFS: Đạt giới hạn {max_nodes} nút.")
                 messagebox.showwarning("Giới hạn", f"Conformant BFS vượt quá giới hạn {max_nodes} belief state được duyệt.", parent=self.root)
                 break

            current_belief_fset, path_of_moves = queue.popleft()
            nodes_expanded += 1

            if nodes_expanded % 100 == 0:
                 self.update_status(f"ConformantBFS: Duyệt {nodes_expanded} belief states...")
                 self.root.update_idletasks()

            for move_delta in moves_deltas:
                if self.stop_flag: break
                next_belief_set = set()
                possible_to_apply_to_all = True

                for state_tuple in current_belief_fset:
                     current_state_np = np.array(state_tuple)
                     next_state_np = self.apply_move(current_state_np, move_delta) # apply_move handles boundaries

                     if next_state_np is not None: # Move was valid for this state
                          next_state_tuple = self.state_to_tuple(next_state_np)
                          if next_state_tuple:
                              next_belief_set.add(next_state_tuple)
                          else: # Should not happen if apply_move is correct
                              possible_to_apply_to_all = False; break
                     else: # Move was invalid for at least one state in belief set
                          possible_to_apply_to_all = False; break
                if not possible_to_apply_to_all: continue # This move is not conformant

                if self.stop_flag: break
                if not next_belief_set: continue

                next_belief_frozenset = frozenset(next_belief_set)

                if next_belief_frozenset not in visited_belief_states:
                    is_goal_belief = all(st == goal_tuple for st in next_belief_frozenset)
                    if is_goal_belief:
                         self.update_status(f"ConformantBFS: Tìm thấy đích sau {nodes_expanded} belief states.")
                         final_path_of_moves = path_of_moves + [move_delta]
                         # Convert path of moves to path of states for display
                         solution_states = []
                         current_s = self.initial_belief_states[0].copy() 
                         for move in final_path_of_moves:
                             next_s = self.apply_move(current_s, move)
                             if next_s is not None:
                                 solution_states.append(next_s.tolist())
                                 current_s = next_s
                             else: # Should not happen if moves are conformant
                                 # print("Error generating state path for conformant solution")
                                 return None, nodes_expanded # Error
                         return solution_states, nodes_expanded

                    visited_belief_states.add(next_belief_frozenset)
                    new_path_of_moves = path_of_moves + [move_delta]
                    queue.append((next_belief_frozenset, new_path_of_moves))

        if self.stop_flag: return None, nodes_expanded
        self.update_status(f"ConformantBFS: Không tìm thấy giải pháp sau {nodes_expanded} belief states.")
        return None, nodes_expanded


    # --- Solve Puzzle Orchestration ---
    def solve_puzzle(self):
        if self.is_belief_mode:
             if not self.initial_belief_states:
                 messagebox.showerror("Lỗi", "Chưa có trạng thái ban đầu cho Belief Mode.", parent=self.root)
                 return
        else: # Standard mode
             if self.start_state is None:
                 messagebox.showerror("Lỗi", "Chưa có trạng thái ban đầu cho chế độ chuẩn.", parent=self.root)
                 return
             if not self.is_solvable(self.start_state):
                 messagebox.showerror("Lỗi", "Trạng thái ban đầu (chuẩn) không thể giải được!")
                 return

        self.stop_flag = False
        algo = self.algo_var.get()
        solution = None # This will be a list of states (np.array.tolist())
        nodes_expanded = 0 # Or steps, or episodes for RL

        # Mode and algorithm compatibility checks
        if algo == "ConformantBFS" and not self.is_belief_mode:
            messagebox.showerror("Lỗi Chế Độ", "Chọn chế độ Belief Mode để chạy Conformant BFS.")
            return
        if algo != "ConformantBFS" and self.is_belief_mode:
            
            messagebox.showerror("Lỗi Chế Độ", f"Thuật toán {algo} hiện không hỗ trợ chế độ Belief Mode.\nHãy chọn chế độ Chuẩn hoặc thuật toán ConformantBFS.")
            return


        self.update_status(f"Đang chạy thuật toán {algo}...")
        self.clear_solution_path_display()
        self.set_button_states(is_running=True)
        start_time = time.time()
        try:
            if algo == "ConformantBFS": solution, nodes_expanded = self.conformant_bfs_solve() # Returns path of states
            elif algo == "BFS": solution, nodes_expanded = self.bfs_solve()
            elif algo == "DFS": solution, nodes_expanded = self.dfs_solve()
            elif algo == "UCS": solution, nodes_expanded = self.ucs_solve()
            elif algo == "IDDFS": solution, nodes_expanded = self.iddfs_solve()
            elif algo == "Greedy": solution, nodes_expanded = self.greedy_solve()
            elif algo == "A*": solution, nodes_expanded = self.a_star_solve()
            elif algo == "IdA*": solution, nodes_expanded = self.ida_star_solve()
            elif algo == "Hill": solution, nodes_expanded = self.hill_climbing_solve()
            elif algo == "Stp_Hill": solution, nodes_expanded = self.stp_hill_solve()
            elif algo == "StochasticHill": solution, nodes_expanded = self.stochastic_hill_climbing_solve()
            elif algo == "SimAnneal": solution, nodes_expanded = self.simulated_annealing_solve()
            elif algo == "BeamSearch": solution, nodes_expanded = self.beam_search_solve()
            elif algo == "AndOrSearch":  solution, nodes_expanded = self.and_or_search_solve()
            elif algo == "GeneticAlg":
                best_state_list, generations = self.genetic_algorithm_solve() # Returns list containing best state
                nodes_expanded = generations
                if best_state_list and np.array_equal(np.array(best_state_list[0]), self.goal_state):
                    solution = best_state_list # Path is just the goal state
                else:
                    solution = None 
                    if best_state_list :
                         self.update_grid(self.start_grid, np.array(best_state_list[0])) # Show best found
                         # No animation for non-solution GA
            elif algo == "Backtracking": solution, nodes_expanded = self.backtracking_solve()
            elif algo == "ForwardChecking": solution, nodes_expanded = self.forward_checking_solve()
            elif algo == "QLearning": solution, nodes_expanded = self.q_learning_solve() # nodes_expanded = episodes

            else:
                messagebox.showinfo("Info", f"{algo} chưa được triển khai!")
                solution = None; nodes_expanded = 0
        except Exception as e:
             messagebox.showerror("Lỗi Thuật Toán", f"Đã xảy ra lỗi trong khi chạy {algo}:\n{e}")
             import traceback
             traceback.print_exc()
             solution = None
             self.update_status(f"Lỗi khi chạy {algo}: {e}")
        end_time = time.time()
        duration = end_time - start_time

        

        if self.stop_flag:
             self.update_status(f"Đã dừng {algo}. Thời gian: {duration:.2f}s. Nút/Bước/Episode: {nodes_expanded}")
             messagebox.showinfo("Thông báo", f"Thuật toán {algo} đã bị dừng.\nThời gian: {duration:.4f}s.\nSố nút/bước/episode: {nodes_expanded}")
        elif solution is not None and solution: # Ensure solution is not empty
            
            if algo == "GeneticAlg":
                num_steps = 0 # GA doesn't have "steps" in the same way
                if np.array_equal(np.array(solution[0]), self.goal_state): # solution[0] is the goal
                     self.update_status(f"{algo}: Tìm thấy đích! Thời gian: {duration:.2f}s. Thế hệ: {nodes_expanded}")
                     messagebox.showinfo("Thành công", f"Genetic Algorithm tìm thấy trạng thái đích.\nThời gian: {duration:.4f} giây.\nSố thế hệ: {nodes_expanded}")
                     self.display_solution_path([self.start_state.tolist(), solution[0]]) # Display start and goal
                     self.animate_solution([self.start_state.tolist(), solution[0]]) # Animate start to goal
                else: # GA did not find the goal, solution might be the best found
                     self.update_status(f"{algo}: Hoàn thành. Best H={self.get_selected_heuristic(np.array(solution[0]))}. Thời gian: {duration:.2f}s. Thế hệ: {nodes_expanded}")
                     messagebox.showinfo("Hoàn thành (GA)", f"Genetic Algorithm hoàn thành.\nTrạng thái tốt nhất có H={self.get_selected_heuristic(np.array(solution[0]))}.\nThời gian: {duration:.4f}s.\nSố thế hệ: {nodes_expanded}")
                     # No animation, grid already updated by GA itself.
            elif algo == "QLearning":
                 num_steps = len(solution) # Path from Q-table
                 self.update_status(f"{algo}: Tìm thấy giải pháp sau {num_steps} bước. Thời gian: {duration:.2f}s. Episodes: {nodes_expanded}")
                 messagebox.showinfo("Thành công (QL)", f"QLearning tìm thấy giải pháp sau {num_steps} bước (từ Q-table).\nThời gian: {duration:.4f}s.\nSố Episodes huấn luyện: {nodes_expanded}")
                 self.display_solution_path(solution) # QL path should include start state
                 self.animate_solution(solution)
            else: # Standard path-finding algorithms
                 num_steps = len(solution) # Number of states in the path (excluding start if not included by algo)
                 # Most algos return path from state AFTER start_state.
                 # display_solution_path prepends start_state. So num_steps is correct.
                 self.update_status(f"{algo}: Thành công! {num_steps} bước. Thời gian: {duration:.2f}s. Nút/Bước: {nodes_expanded}")
                 messagebox.showinfo("Thành công", f"Tìm thấy giải pháp bằng {algo} sau {num_steps} bước.\nThời gian: {duration:.4f} giây.\nSố nút/bước đã duyệt: {nodes_expanded}")
                 self.display_solution_path(solution) # display_solution_path adds start_state
                 self.animate_solution([self.start_state.tolist()] + solution)

        else: # solution is None or empty, and not stopped
            if algo not in ["GeneticAlg"]: # GA has its own message if no goal
                 self.update_status(f"{algo}: Thất bại hoặc không tìm thấy. Thời gian: {duration:.2f}s. Nút/Bước/Episode: {nodes_expanded}")
                 messagebox.showerror("Thất bại", f"Không tìm thấy giải pháp bằng {algo}.\nThời gian: {duration:.4f} giây.\nSố nút/bước/episode đã duyệt: {nodes_expanded}")

        self.set_button_states(is_running=False)

    # --- Search Algorithms Helper ---
    def get_neighbors(self, state_np): # Expects np.array
        neighbors = []
        zero_pos_list = np.argwhere(state_np == 0)
        if not zero_pos_list.size > 0: return []
        zero_pos = zero_pos_list[0]
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)] # U, D, L, R

        for move_delta in moves:
            new_pos = zero_pos + np.array(move_delta)
            if 0 <= new_pos[0] < 3 and 0 <= new_pos[1] < 3:
                new_state = state_np.copy()
                new_state[zero_pos[0], zero_pos[1]], new_state[new_pos[0], new_pos[1]] = \
                    new_state[new_pos[0], new_pos[1]], new_state[zero_pos[0], zero_pos[1]]
                neighbors.append(new_state)
        return neighbors

    def check_stop_condition(self, count, check_interval=50):
        if self.stop_flag: return True
        if count % check_interval == 0 and count > 0 : # Avoid update at count 0
            algo_name = self.algo_var.get() if hasattr(self, 'algo_var') else "Algorithm"
            self.update_status(f"{algo_name}: Đã xử lý {count} nút/bước/episodes...")
            if self.root.winfo_exists(): self.root.update_idletasks() # Allow GUI to process stop
        return False

    

    def bfs_solve(self):
        visited = set()
        start_tuple = self.state_to_tuple(self.start_state)
        if start_tuple is None: return None, 0

        queue = deque([(start_tuple, [])]) # path is list of states (as list of lists)
        visited.add(start_tuple)
        nodes_expanded = 0
        check_interval = 200

        while queue:
            if self.check_stop_condition(nodes_expanded, check_interval): break
            state_tuple, path = queue.popleft()
            current_state_np = np.array(state_tuple)
            nodes_expanded += 1

            if np.array_equal(current_state_np, self.goal_state): return path, nodes_expanded

            for neighbor_state_np in self.get_neighbors(current_state_np):
                neighbor_tuple = self.state_to_tuple(neighbor_state_np)
                if neighbor_tuple and neighbor_tuple not in visited:
                    visited.add(neighbor_tuple)
                    new_path = path + [neighbor_state_np.tolist()]
                    queue.append((neighbor_tuple, new_path))
        return None, nodes_expanded


    def dfs_solve(self, depth_limit=35): 
        visited_depths = {} # state_tuple -> min_depth_found
        start_tuple = self.state_to_tuple(self.start_state)
        if start_tuple is None: return None, 0

        stack = [(start_tuple, [], 0)]
        visited_depths[start_tuple] = 0
        nodes_expanded = 0
        check_interval = 500

        while stack:
            if self.check_stop_condition(nodes_expanded, check_interval): break
            state_tuple, path, depth = stack.pop()
            current_state_np = np.array(state_tuple)
            nodes_expanded += 1

            if np.array_equal(current_state_np, self.goal_state): return path, nodes_expanded
            if depth >= depth_limit: continue

            
            neighbors_list = self.get_neighbors(current_state_np)
            for neighbor_state_np in reversed(neighbors_list):
                neighbor_tuple = self.state_to_tuple(neighbor_state_np)
                if neighbor_tuple:
                    new_depth = depth + 1
                    if new_depth < visited_depths.get(neighbor_tuple, float('inf')): 
                        visited_depths[neighbor_tuple] = new_depth
                        new_path = path + [neighbor_state_np.tolist()]
                        stack.append((neighbor_tuple, new_path, new_depth))
        return None, nodes_expanded


    def ucs_solve(self):
        # ... (no change for heuristics, uses np.array and state_to_tuple)
        start_tuple = self.state_to_tuple(self.start_state)
        if start_tuple is None: return None, 0

        priority_queue = [(0, start_tuple, [])] 
        visited_costs = {start_tuple: 0} 
        nodes_expanded = 0
        check_interval = 200

        while priority_queue:
            if self.check_stop_condition(nodes_expanded, check_interval): break
            cost, state_tuple, path = heapq.heappop(priority_queue)
            current_state_np = np.array(state_tuple)

            if cost > visited_costs.get(state_tuple, float('inf')): continue # Already found shorter path
            nodes_expanded += 1
            if np.array_equal(current_state_np, self.goal_state): return path, nodes_expanded

            for neighbor_state_np in self.get_neighbors(current_state_np):
                 neighbor_tuple = self.state_to_tuple(neighbor_state_np)
                 if neighbor_tuple:
                    new_cost = cost + 1 # Assuming cost of each move is 1
                    if new_cost < visited_costs.get(neighbor_tuple, float('inf')):
                        visited_costs[neighbor_tuple] = new_cost
                        new_path = path + [neighbor_state_np.tolist()]
                        heapq.heappush(priority_queue, (new_cost, neighbor_tuple, new_path))
        return None, nodes_expanded

    def iddfs_solve(self, max_depth_iddfs=35): # Renamed max_depth to avoid conflict
        # ... (no change for heuristics, uses np.array and state_to_tuple)
        total_nodes_expanded = 0
        self.update_status("Bắt đầu IDDFS...")
        for depth_limit_dls in range(max_depth_iddfs + 1): # Renamed depth
            if self.stop_flag: break
            self.update_status(f"IDDFS: Đang tìm ở độ sâu {depth_limit_dls}...")
            visited_this_dls = set() # Visited set for current DLS iteration
            start_tuple = self.state_to_tuple(self.start_state)
            if start_tuple is None: return None, total_nodes_expanded

            # DLS needs to handle its own path construction from start
            result_path, nodes_dls = self.dls_recursive(start_tuple, [], visited_this_dls, depth_limit_dls, 0)
            total_nodes_expanded += nodes_dls

            if self.stop_flag: break
            if result_path is not None:
                self.update_status(f"IDDFS: Tìm thấy ở độ sâu {depth_limit_dls}.")
                return result_path, total_nodes_expanded
        status_msg = "Đã dừng." if self.stop_flag else f"Không tìm thấy trong giới hạn độ sâu {max_depth_iddfs}."
        self.update_status(f"IDDFS: {status_msg}")
        return None, total_nodes_expanded

    def dls_recursive(self, state_tuple, path_so_far, visited_dls, depth_limit, current_d):
        nodes_expanded_this_branch = 1 # Count current node
        if self.stop_flag: return None, nodes_expanded_this_branch

        current_state_np = np.array(state_tuple)
        if np.array_equal(current_state_np, self.goal_state):
            return path_so_far, nodes_expanded_this_branch # Path found

        if current_d >= depth_limit:
            return None, nodes_expanded_this_branch 

        visited_dls.add(state_tuple)


        if nodes_expanded_this_branch % 500 == 0 : 
             if self.root.winfo_exists(): self.root.update_idletasks()
             if self.stop_flag: return None, nodes_expanded_this_branch

        for neighbor_state_np in self.get_neighbors(current_state_np):
             neighbor_tuple = self.state_to_tuple(neighbor_state_np)
             if neighbor_tuple and neighbor_tuple not in visited_dls: 
                  new_path = path_so_far + [neighbor_state_np.tolist()]
                  # visited_dls.add(neighbor_tuple) # Add before recursive call
                  result_path, nodes_from_child = self.dls_recursive(
                      neighbor_tuple, new_path, visited_dls, depth_limit, current_d + 1
                  )
                  nodes_expanded_this_branch += nodes_from_child
                  if result_path is not None: return result_path, nodes_expanded_this_branch
                  if self.stop_flag: return None, nodes_expanded_this_branch
                  
                                                    
        return None, nodes_expanded_this_branch

    # --- Greedy ---
    def greedy_solve(self):
        start_tuple = self.state_to_tuple(self.start_state)
        if start_tuple is None: return None, 0

        h_cost = self.heuristic_manhattan(self.start_state)
        priority_queue = [(h_cost, start_tuple, [])] 
        visited = set() 
        nodes_expanded = 0
        check_interval = 200

        while priority_queue:
            if self.check_stop_condition(nodes_expanded, check_interval): break

            h, state_tuple, path = heapq.heappop(priority_queue)

            # Kiểm tra visited sau khi lấy ra khỏi queue
            if state_tuple in visited: continue
            visited.add(state_tuple)

            current_state = np.array(state_tuple)
            nodes_expanded += 1

            if np.array_equal(current_state, self.goal_state): return path, nodes_expanded

            for neighbor_state in self.get_neighbors(current_state):
                 neighbor_tuple = self.state_to_tuple(neighbor_state)
                 if neighbor_tuple and neighbor_tuple not in visited:
                    new_h_cost = self.heuristic_manhattan(neighbor_state)
                    new_path = path + [neighbor_state.tolist()]
                    heapq.heappush(priority_queue, (new_h_cost, neighbor_tuple, new_path))

        return None, nodes_expanded


    
    def a_star_solve(self):
        start_tuple = self.state_to_tuple(self.start_state)
        if start_tuple is None: return None, 0

        g_cost = 0
        h_cost = self.heuristic_manhattan(self.start_state)
        f_cost = g_cost + h_cost
        priority_queue = [(f_cost, g_cost, start_tuple, [])] 
        visited = {start_tuple: g_cost}
        nodes_expanded = 0
        check_interval = 200

        while priority_queue:
            if self.check_stop_condition(nodes_expanded, check_interval): break

            f, current_g_cost, state_tuple, path = heapq.heappop(priority_queue)
            current_state = np.array(state_tuple)

            
            if current_g_cost > visited.get(state_tuple, float('inf')): continue

            nodes_expanded += 1
            if np.array_equal(current_state, self.goal_state): return path, nodes_expanded

            for neighbor_state in self.get_neighbors(current_state):
                 neighbor_tuple = self.state_to_tuple(neighbor_state)
                 if neighbor_tuple:
                    new_g_cost = current_g_cost + 1 # Chi phí bước là 1
                    # Chỉ xét nếu chưa thăm hoặc tìm được đường đi tốt hơn
                    if new_g_cost < visited.get(neighbor_tuple, float('inf')):
                        visited[neighbor_tuple] = new_g_cost
                        new_h_cost = self.heuristic_manhattan(neighbor_state)
                        new_f_cost = new_g_cost + new_h_cost
                        new_path = path + [neighbor_state.tolist()]
                        heapq.heappush(priority_queue, (new_f_cost, new_g_cost, neighbor_tuple, new_path))

        return None, nodes_expanded


    
    def ida_star_solve(self):
        """Triển khai IDA*."""
        threshold = self.heuristic_manhattan(self.start_state)
        
        total_nodes_expanded = 0
        self.update_status(f"Bắt đầu IDA* với ngưỡng {threshold}...")

        while not self.stop_flag:
            
            
            start_tuple = self.state_to_tuple(self.start_state)
            if start_tuple is None: return None, total_nodes_expanded

            path_tuples_this_iter = {start_tuple}

            result, new_threshold, nodes_expanded_iter = self.ida_search_recursive(
                start_tuple, [], path_tuples_this_iter, 0, threshold, check_stop_interval=1000 # Check ít hơn
            )
            total_nodes_expanded += nodes_expanded_iter

            if result is not None: 
                 if self.stop_flag: return None, total_nodes_expanded 
                 self.update_status(f"IDA*: Tìm thấy giải pháp.")
                 # print(f"IDA* SUCCESS: Path found with f={threshold}") # Debug
                 return result, total_nodes_expanded

            if new_threshold == float('inf'): 
                 self.update_status(f"IDA*: Không tìm thấy giải pháp.")
                 # print(f"IDA* FAILED: min_exceeding_cost is infinity") # Debug
                 return None, total_nodes_expanded

            if self.stop_flag: # Bị dừng trong lần lặp
                 self.update_status(f"IDA*: Đã dừng.")
                 # print(f"IDA* STOPPED") # Debug
                 return None, total_nodes_expanded

            if new_threshold <= threshold: 
                 print(f"Warning: IDA* new threshold {new_threshold} <= old threshold {threshold}. Stopping.")
                 self.update_status(f"IDA*: Lỗi ngưỡng, dừng.")
                 return None, total_nodes_expanded

            threshold = new_threshold 
            self.update_status(f"IDA*: Tăng ngưỡng lên {threshold}...")
            # print(f"IDA* Increasing Threshold to: {threshold}") # Debug
            

        return None, total_nodes_expanded 


    def ida_search_recursive(self, current_tuple, current_path_list, path_tuples_this_iter, g, threshold, check_stop_interval):
        """Hàm đệ quy cho IDA*."""
        nodes_expanded = 1
        current_state = np.array(current_tuple)
        h = self.heuristic_manhattan(current_state)
        f = g + h

        if f > threshold:
            return None, f, nodes_expanded 

        if np.array_equal(current_state, self.goal_state):
            return current_path_list, threshold, nodes_expanded 

        # Check stop định kỳ
        if nodes_expanded % check_stop_interval == 0:
            # self.root.update_idletasks() 
            if self.stop_flag: return None, float('inf'), nodes_expanded # Bị dừng

        min_exceeding_cost = float('inf') 

        for neighbor_state in self.get_neighbors(current_state):
             neighbor_tuple = self.state_to_tuple(neighbor_state)
             if neighbor_tuple and neighbor_tuple not in path_tuples_this_iter:
                  # Thêm vào path và visited cho nhánh đệ quy này
                  path_tuples_this_iter.add(neighbor_tuple)
                  new_path = current_path_list + [neighbor_state.tolist()]

                  solution_path, exceeding_cost, nodes_in_branch = self.ida_search_recursive(
                      neighbor_tuple, new_path, path_tuples_this_iter, g + 1, threshold, check_stop_interval
                  )
                  nodes_expanded += nodes_in_branch

                  
                  path_tuples_this_iter.remove(neighbor_tuple)

                  if solution_path is not None: 
                       return solution_path, threshold, nodes_expanded
                  if exceeding_cost == float('inf') and self.stop_flag: 
                       return None, float('inf'), nodes_expanded

                  
                  min_exceeding_cost = min(min_exceeding_cost, exceeding_cost)

                  
                  if self.stop_flag: return None, float('inf'), nodes_expanded


        
        return None, min_exceeding_cost, nodes_expanded


    
    def hill_climbing_solve(self, max_iterations=1000, steepest=False, stochastic=False):
        """Hill climbing (Simple, Steepest, Stochastic)."""
        mode = "Steepest" if steepest else ("Stochastic" if stochastic else "Simple")
        self.update_status(f"Bắt đầu {mode} Hill Climbing...")

        current_state = self.start_state.copy()
        path = [] 
        steps = 0 

        for i in range(max_iterations):
            if self.check_stop_condition(i, 50): break 
            steps += 1
            current_h = self.heuristic_manhattan(current_state)

            if current_h == 0:
                 self.update_status(f"{mode} Hill Climbing: Đã đạt trạng thái đích sau {i} bước.")
                 return path, steps

            neighbors = self.get_neighbors(current_state)
            if not neighbors: break 

            best_neighbor = None
            best_neighbor_h = current_h
            better_neighbors = [] 

            for neighbor in neighbors:
                 neighbor_h = self.heuristic_manhattan(neighbor)
                 if neighbor_h < current_h:
                     better_neighbors.append((neighbor, neighbor_h)) 
                     if steepest:
                         if neighbor_h < best_neighbor_h:
                             best_neighbor_h = neighbor_h
                             best_neighbor = neighbor.copy()
                     elif not steepest and not stochastic: 
                         best_neighbor_h = neighbor_h
                         best_neighbor = neighbor.copy()
                         break 

            
            move_made = False
            if steepest:
                 if best_neighbor is not None: 
                     current_state = best_neighbor
                     path.append(current_state.tolist())
                     move_made = True
            elif stochastic:
                 if better_neighbors: 
                     chosen_neighbor, best_neighbor_h = random.choice(better_neighbors)
                     current_state = chosen_neighbor.copy()
                     path.append(current_state.tolist())
                     move_made = True
            else: # Simple
                 if best_neighbor is not None: 
                     current_state = best_neighbor
                     path.append(current_state.tolist())
                     move_made = True

            if not move_made: 
                 self.update_status(f"{mode} Hill Climbing: Bị kẹt ở bước {i} (h={current_h}).")
                 messagebox.showinfo(f"{mode} Hill Climbing", f"Bị kẹt (không tìm thấy bước đi tốt hơn) ở bước {i}.", parent=self.root)
                 
                 if path: self.animate_solution([self.start_state.tolist()] + path)
                 return None, steps 

            
            if i % 5 == 0: 
                 self.update_grid(self.start_grid, current_state)
                 self.update_status(f"{mode} Hill Climbing: Bước {i}, h={best_neighbor_h}")
                 self.root.update_idletasks()

        
        if self.stop_flag: return None, steps
        final_h = self.heuristic_manhattan(current_state)
        if final_h == 0: return path, steps 

        self.update_status(f"{mode} Hill Climbing: Đạt giới hạn {max_iterations} lần lặp (h={final_h}).")
        messagebox.showinfo(f"{mode} Hill Climbing", f"Đạt giới hạn {max_iterations} lần lặp.", parent=self.root)
        if path: self.animate_solution([self.start_state.tolist()] + path) 
        return None, steps


    def stp_hill_solve(self, max_iterations=1000):
         return self.hill_climbing_solve(max_iterations, steepest=True)

    def stochastic_hill_climbing_solve(self, max_iterations=2000):
         return self.hill_climbing_solve(max_iterations, stochastic=True)


    # --- Simulated Annealing ---
    def simulated_annealing_solve(self, initial_temp=100, cooling_rate=0.995, min_temp=0.1, max_iter=10000): 
        current_state = self.start_state.copy()
        current_h = self.heuristic_manhattan(current_state)
        best_state = current_state.copy() 
        best_h = current_h
        path_to_current = [] 
        path_to_best = []    

        temp = initial_temp
        iterations = 0
        self.update_status(f"Bắt đầu SimAnneal (T={temp:.2f})...")
        check_interval = 100 

        while temp > min_temp and iterations < max_iter:
            if self.check_stop_condition(iterations, check_interval): break
            iterations += 1

            # Tạo neighbor ngẫu nhiên
            neighbors = self.get_neighbors(current_state)
            if not neighbors: break
            next_state = random.choice(neighbors)
            next_h = self.heuristic_manhattan(next_state)

            if next_h < best_h:
                best_h = next_h
                best_state = next_state.copy()
                path_to_best = path_to_current + [next_state.tolist()] 
                if best_h == 0: 
                     self.update_status(f"SimAnneal: Tìm thấy đích sau {iterations} bước (h=0).")
                     
                     return path_to_best, iterations


            delta_e = next_h - current_h
            move = False
            if delta_e < 0:
                move = True
            elif temp > 1e-9: 
                 try:
                     acceptance_prob = math.exp(-delta_e / temp)
                     if random.random() < acceptance_prob: move = True
                 except OverflowError: move = False 

            if move:
                 current_state = next_state.copy()
                 current_h = next_h
                 path_to_current.append(current_state.tolist()) 
                 if iterations % 5 == 0: 
                      self.update_grid(self.start_grid, current_state)
                      
            temp *= cooling_rate

        
        if self.stop_flag: return None, iterations

        
        if best_h == 0:
             self.update_status(f"SimAnneal: Tìm thấy đích (h=0) sau {iterations} bước.")
             return path_to_best, iterations 

        # Không tìm thấy đích
        self.update_status(f"SimAnneal: Kết thúc (T={temp:.2f}, best_h={best_h}, iter={iterations}).")
        messagebox.showinfo("Simulated Annealing", f"Không tìm thấy đích sau {iterations} lần lặp (có thể bị kẹt).\nTrạng thái tốt nhất có h={best_h}.")
        
        if path_to_best: self.animate_solution([self.start_state.tolist()] + path_to_best)
        return None, iterations


    
    def beam_search_solve(self, beam_width=10, max_depth=50): 
         start_tuple = self.state_to_tuple(self.start_state)
         if start_tuple is None: return None, 0
         start_h = self.heuristic_manhattan(self.start_state)

         
         beam = [(start_h, start_tuple, [])]
         
         visited_globally = {start_tuple}
         nodes_expanded_total = 0
         depth = 0
         check_interval = 1 

         self.update_status(f"Bắt đầu Beam Search (k={beam_width})...")

         while beam and depth < max_depth:
             if self.check_stop_condition(depth, check_interval): break 
             depth += 1
             successors = []
             nodes_expanded_level = 0
             
             successor_tuples_this_level = set()

             for h, state_tuple, path in beam:
                 current_state = np.array(state_tuple)
                 nodes_expanded_total += 1 
                 nodes_expanded_level += 1

                 
                 if h == 0 and np.array_equal(current_state, self.goal_state):
                      self.update_status(f"Beam Search: Tìm thấy đích ở độ sâu {len(path)}.")
                      return path, nodes_expanded_total

                 for neighbor_state in self.get_neighbors(current_state):
                     neighbor_tuple = self.state_to_tuple(neighbor_state)
                     
                     if neighbor_tuple and neighbor_tuple not in visited_globally and neighbor_tuple not in successor_tuples_this_level:
                          neighbor_h = self.heuristic_manhattan(neighbor_state)
                          new_path = path + [neighbor_state.tolist()]
                          successors.append((neighbor_h, neighbor_tuple, new_path))
                          successor_tuples_this_level.add(neighbor_tuple)


             if self.stop_flag: break
             if not successors: break 

            
             successors.sort(key=lambda x: x[0])
             beam = successors[:beam_width]

             
             for _, tuple_succ, _ in beam:
                 visited_globally.add(tuple_succ)

             self.update_status(f"Beam Search: Độ sâu {depth}, Beam size={len(beam)}, Nodes(total)={nodes_expanded_total}")
             

         
         if self.stop_flag: return None, nodes_expanded_total

         
         for h, state_tuple, path in beam:
            if h == 0 and np.array_equal(np.array(state_tuple), self.goal_state):
                 self.update_status(f"Beam Search: Tìm thấy đích ở độ sâu {len(path)}.")
                 return path, nodes_expanded_total

         self.update_status(f"Beam Search: Kết thúc ở độ sâu {depth}. Không tìm thấy đích.")
         messagebox.showinfo("Beam Search", f"Không tìm thấy đích sau {depth} bước (beam có thể rỗng hoặc đạt giới hạn).")
         return None, nodes_expanded_total

    
    def and_or_search_solve(self, depth_limit=25): 
        self.update_status("Bắt đầu AndOrSearch (Mô phỏng DFS)...")
        start_node = self.start_state
        start_tuple = self.state_to_tuple(start_node)
        if start_tuple is None: return None, 0

        path_tuples = {start_tuple} 
        self._and_or_result_path = None

        found, nodes_expanded = self._and_or_recursive_search(start_tuple, [], path_tuples, depth_limit, 0)

        if found and self._and_or_result_path is not None:
             return self._and_or_result_path, nodes_expanded
        else:
             if not self.stop_flag:
                  messagebox.showinfo("AndOrSearch", f"Không tìm thấy giải pháp trong giới hạn độ sâu {depth_limit}.")
                  self.update_status(f"AndOrSearch: Không tìm thấy (giới hạn độ sâu {depth_limit}).")
             return None, nodes_expanded

    def _and_or_recursive_search(self, current_tuple, current_path_list, visited_path_tuples, depth_limit, current_depth):
        
        nodes_expanded = 1
        if self.check_stop_condition(nodes_expanded, 100):
             return False, nodes_expanded

        current_state = np.array(current_tuple)
        if np.array_equal(current_state, self.goal_state):
            self._and_or_result_path = current_path_list 
            return True, nodes_expanded

        if current_depth >= depth_limit:
            return False, nodes_expanded

        
        neighbors = self.get_neighbors(current_state)
        

        for neighbor_state in neighbors:
            neighbor_tuple = self.state_to_tuple(neighbor_state)

            if neighbor_tuple and neighbor_tuple not in visited_path_tuples:
                visited_path_tuples.add(neighbor_tuple)
                new_path = current_path_list + [neighbor_state.tolist()]

                

                found, nodes_in_branch = self._and_or_recursive_search(
                    neighbor_tuple, new_path, visited_path_tuples, depth_limit, current_depth + 1
                )
                nodes_expanded += nodes_in_branch

                if found: return True, nodes_expanded 
                if self.stop_flag: return False, nodes_expanded 

                
                visited_path_tuples.remove(neighbor_tuple)

                
                if self.stop_flag: return False, nodes_expanded


        return False, nodes_expanded 


# --- Genetic Algorithm ---
    def genetic_algorithm_solve(self, population_size=50, generations=100, mutation_rate=0.2, tournament_size=5, elite_size=0.1): # Added elite_size
        self.update_status("Bắt đầu Genetic Algorithm...")

        # Use the class's selected heuristic via the helper method
        def calculate_fitness_ga(state_np_eval): # Renamed for clarity
            dist = self.get_selected_heuristic(state_np_eval) # USE SELECTED HEURISTIC
            # Higher fitness for lower heuristic cost (goal has h=0)
            if dist == 0:
                return 1000.0  # Distinctly high fitness for the goal state
            return 1.0 / (1.0 + float(dist))

        # Your crossover function (assuming it's part of the class or accessible)
        # It should take two parent states (e.g., numpy arrays) and return a child state (numpy array)
        def perform_crossover(parent1_state_np, parent2_state_np):
            # This is based on the crossover you provided earlier (flatten, cut, fill)
            p1_flat = parent1_state_np.flatten().tolist()
            p2_flat = parent2_state_np.flatten().tolist()
            
            # Ensure 9 unique numbers 0-8 if not already guaranteed
            # This basic crossover might produce invalid lists if not handled carefully
            # For 8-puzzle, PMX (Partially Mapped Crossover) or Order Crossover are common for permutations.
            # Using a simpler one-point for flattened lists:
            cut_point = random.randint(1, 7) # Cut between 1 and 7 for a 9-element list
            
            child_flat_part1 = p1_flat[:cut_point]
            child_flat_part2 = []
            for gene in p2_flat:
                if gene not in child_flat_part1:
                    child_flat_part2.append(gene)
            
            child_flat = child_flat_part1 + child_flat_part2
            # Ensure the child_flat is the correct length and has all numbers
            # This simple crossover might need refinement to always produce a valid permutation of 0-8
            # For robustness, if child_flat isn't a valid permutation, might return one of the parents
            # or use a more sophisticated permutation crossover.
            # For now, let's assume it produces a list of 9 unique numbers.
            if len(child_flat) == 9 and len(set(child_flat)) == 9:
                 child_unflattened = np.array(child_flat).reshape((3,3))
                 # IMPORTANT: Check solvability of the new child from crossover
                 if self.is_solvable(child_unflattened):
                     return child_unflattened
            # Fallback if crossover fails or produces unsolvable: return a copy of one parent
            return parent1_state_np.copy()


        population = []
        # Use a set of tuples to track states in the current population to avoid duplicates if desired
        # population_tuples_set = set() # To avoid adding exact same state multiple times initially

        start_tuple = self.state_to_tuple(self.start_state)
        if start_tuple is None: return None, 0

        # Add initial start state
        if self.is_solvable(self.start_state): # Should always be true if input is validated
            population.append({'state': self.start_state.copy(),
                               'fitness': calculate_fitness_ga(self.start_state)})
            # population_tuples_set.add(start_tuple)

        # Generate initial population with diverse *SOLVABLE* states
        # (Using random walks from start_state is one way, ensuring solvability)
        q = deque([(self.start_state.copy(), 0)]) # state, depth_of_walk
        visited_init_tuples = {start_tuple}

        while len(population) < population_size and q:
            current_s_init, depth_init = q.popleft()
            if len(population) >= population_size: break
            if depth_init > 5 : continue # Limit random walk depth for initial pop

            for _ in range(3): # Try a few random moves from current_s_init to diversify
                neighbors_init = self.get_neighbors(current_s_init)
                if not neighbors_init: continue
                
                new_potential_state = random.choice(neighbors_init)
                new_potential_tuple = self.state_to_tuple(new_potential_state)

                if new_potential_tuple not in visited_init_tuples:
                    visited_init_tuples.add(new_potential_tuple)
                    # CRITICAL FIX: Ensure solvability
                    if self.is_solvable(new_potential_state):
                        population.append({'state': new_potential_state.copy(),
                                           'fitness': calculate_fitness_ga(new_potential_state)})
                        if len(population) >= population_size: break
                        q.append((new_potential_state.copy(), depth_init + 1))
                if len(population) >= population_size: break
            if len(population) >= population_size: break
        
        # If population is still too small, you might need a robust random solvable board generator.
        # For now, we proceed even if smaller than population_size.

        if not population: # Should not happen if start_state is valid
            messagebox.showerror("GA Lỗi", "Không thể khởi tạo population hợp lệ.")
            return None, 0


        best_overall_fitness = -1.0  # Maximize fitness
        # Store the state as a list of lists for consistency with other path formats
        best_overall_state_list = self.start_state.tolist() 
        gen = 0
        check_interval_ga = max(1, generations // 20)


        for gen in range(generations):
            if self.check_stop_condition(gen, check_interval_ga): break

            # --- Calculate fitness for current population ---
            goal_found_this_gen = False
            current_gen_best_fitness = -1.0
            current_gen_best_state_np = None

            for individual in population:
                # Fitness might have been calculated when individuals were created/mutated
                # but recalculating ensures consistency if fitness function changes or state was altered
                individual['fitness'] = calculate_fitness_ga(individual['state'])
                if individual['fitness'] > current_gen_best_fitness:
                    current_gen_best_fitness = individual['fitness']
                    current_gen_best_state_np = individual['state']

                if individual['fitness'] >= 1000.0:  # Check against the high value for goal
                    best_overall_state_list = individual['state'].tolist()
                    best_overall_fitness = individual['fitness']
                    goal_found_this_gen = True
                    break 
            if goal_found_this_gen: break

            # Update overall best if a better non-goal state is found this generation
            if current_gen_best_fitness > best_overall_fitness:
                best_overall_fitness = current_gen_best_fitness
                if current_gen_best_state_np is not None:
                    best_overall_state_list = current_gen_best_state_np.tolist()
            
            # --- Create Next Generation ---
            next_gen_population = []
            next_gen_tuples = set() # To avoid duplicates in the new generation

            # 1. Elitism
            population.sort(key=lambda x: x['fitness'], reverse=True) # Sort by fitness descending
            num_elites = int(population_size * elite_size)
            elites_to_add = population[:num_elites]

            for elite_ind in elites_to_add:
                elite_tuple = self.state_to_tuple(elite_ind['state'])
                if elite_tuple not in next_gen_tuples: # Should always be true if pop had no dupes
                    next_gen_population.append(copy.deepcopy(elite_ind)) # Carry over fitness too
                    next_gen_tuples.add(elite_tuple)

            # 2. Crossover and Mutation to fill the rest
            while len(next_gen_population) < population_size:
                # Selection (Tournament)
                # Ensure enough individuals for sampling if population became small
                if len(population) < tournament_size : # Fallback if population is too small for tournament
                     if not population: break # Stop if population died out
                     parent1_obj = random.choice(population)
                     parent2_obj = random.choice(population)
                else:
                     tournament1 = random.sample(population, tournament_size)
                     parent1_obj = max(tournament1, key=lambda x: x['fitness'])
                     tournament2 = random.sample(population, tournament_size)
                     parent2_obj = max(tournament2, key=lambda x: x['fitness'])

                # Crossover
                child_state_np = perform_crossover(parent1_obj['state'], parent2_obj['state'])
                # Solvability is now checked inside perform_crossover

                # Mutation
                if random.random() < mutation_rate:
                    possible_moves = self.get_neighbors(child_state_np)
                    if possible_moves:
                        mutated_state = random.choice(possible_moves)
                        # CRITICAL FIX: Ensure solvability after mutation
                        if self.is_solvable(mutated_state):
                            child_state_np = mutated_state.copy()
                        # else: keep the child_state_np from crossover if mutation leads to unsolvable

                child_tuple = self.state_to_tuple(child_state_np)
                if child_tuple not in next_gen_tuples:
                    next_gen_population.append({'state': child_state_np, 
                                                'fitness': calculate_fitness_ga(child_state_np)})
                    next_gen_tuples.add(child_tuple)
                
                if not population: break # Safety break

            population = next_gen_population
            if not population:
                self.update_status(f"GeneticAlg: Thế hệ {gen+1}, Population died out!")
                break 

            # Update status with heuristic of the current best_overall_state_list
            current_best_h = self.get_selected_heuristic(np.array(best_overall_state_list))
            self.update_status(f"GeneticAlg: Thế hệ {gen+1}, Best Fitness in Gen={current_gen_best_fitness:.4f}, Overall Best H={current_best_h:.0f}")

        # --- End of generations ---
        generations_completed = gen + 1
        final_h_of_best = self.get_selected_heuristic(np.array(best_overall_state_list))

        if final_h_of_best == 0: # Check heuristic value for goal
            self.update_status(f"GeneticAlg: Tìm thấy đích ở thế hệ {generations_completed}.")
            return [best_overall_state_list], generations_completed # Return as list of states
        elif self.stop_flag:
            self.update_status(f"GeneticAlg: Dừng ở thế hệ {generations_completed}. Best h={final_h_of_best:.0f}")
            return [best_overall_state_list], generations_completed
        else:
            self.update_status(f"GeneticAlg: Hoàn thành {generations_completed} thế hệ. Best h={final_h_of_best:.0f}.")
            messagebox.showinfo("Genetic Algorithm", f"Hoàn thành {generations_completed} thế hệ. Không tìm thấy trạng thái đích.\nTrạng thái tốt nhất đạt được có h={final_h_of_best:.0f}.")
            return [best_overall_state_list], generations_completed


    def backtracking_solve(self, max_depth_bt=30): 
        self.update_status("Bắt đầu Backtracking Search...")
        start_tuple = self.state_to_tuple(self.start_state)
        if start_tuple is None: return None, 0

        
        visited_states = set()
        
        self._bt_nodes_expanded = 0 
        solution_path = self._backtracking_recursive(start_tuple, [], visited_states, max_depth_bt, 0)
        return solution_path, self._bt_nodes_expanded

    def _backtracking_recursive(self, current_tuple, path_so_far, visited, depth_limit, current_depth):
        self._bt_nodes_expanded += 1
        if self.check_stop_condition(self._bt_nodes_expanded, 100): 
            return None

        current_state_np = np.array(current_tuple)
        if np.array_equal(current_state_np, self.goal_state):
            return path_so_far 

        if current_depth >= depth_limit:
            return None 

        visited.add(current_tuple) 

        for neighbor_np in self.get_neighbors(current_state_np):
            neighbor_tuple = self.state_to_tuple(neighbor_np)
            if neighbor_tuple and neighbor_tuple not in visited:
                new_path = path_so_far + [neighbor_np.tolist()]
                result = self._backtracking_recursive(neighbor_tuple, new_path, visited, depth_limit, current_depth + 1)
                if result is not None:
                    return result 
                if self.stop_flag: return None 
        
        return None


    def forward_checking_solve(self, max_depth_fc=30): 
        self.update_status("Bắt đầu Forward Checking Search...")
        start_tuple = self.state_to_tuple(self.start_state)
        if start_tuple is None: return None, 0

        visited_states_fc = set() 
        self._fc_nodes_expanded = 0
        # Path stores list of states
        solution_path = self._forward_checking_recursive(start_tuple, [], visited_states_fc, max_depth_fc, 0)
        return solution_path, self._fc_nodes_expanded

    def _forward_checking_can_move(self, state_np):
        
        return len(self.get_neighbors(state_np)) > 0

    def _forward_checking_recursive(self, current_tuple, path_so_far, visited, depth_limit, current_depth):
        self._fc_nodes_expanded += 1
        if self.check_stop_condition(self._fc_nodes_expanded, 100):
            return None

        current_state_np = np.array(current_tuple)
        if np.array_equal(current_state_np, self.goal_state):
            return path_so_far

        if current_depth >= depth_limit:
            return None

        visited.add(current_tuple)

        for neighbor_np in self.get_neighbors(current_state_np):
            neighbor_tuple = self.state_to_tuple(neighbor_np)
            if neighbor_tuple and neighbor_tuple not in visited:
                
                if not self.is_solvable(neighbor_np): 
                    continue
                if not self._forward_checking_can_move(neighbor_np): 
                    continue

                new_path = path_so_far + [neighbor_np.tolist()]
                result = self._forward_checking_recursive(neighbor_tuple, new_path, visited, depth_limit, current_depth + 1)
                if result is not None:
                    return result
                if self.stop_flag: return None
        
        return None


    def get_q_learning_params(self):
        params = {}
        try:
            episodes_str = simpledialog.askstring("Q-Learning Tham số", "Số lượng Episodes:", initialvalue="1000", parent=self.root)
            if episodes_str is None: return None
            params['episodes'] = int(episodes_str)

            epsilon_str = simpledialog.askstring("Q-Learning Tham số", "Tỷ lệ Epsilon (0.0 to 1.0):", initialvalue="0.1", parent=self.root)
            if epsilon_str is None: return None
            params['epsilon'] = float(epsilon_str)

            alpha_str = simpledialog.askstring("Q-Learning Tham số", "Tỷ lệ học Alpha (0.0 to 1.0):", initialvalue="0.1", parent=self.root)
            if alpha_str is None: return None
            params['alpha'] = float(alpha_str)

            gamma_str = simpledialog.askstring("Q-Learning Tham số", "Hệ số chiết khấu Gamma (0.0 to 1.0):", initialvalue="0.9", parent=self.root)
            if gamma_str is None: return None
            params['gamma'] = float(gamma_str)

            if not (0 <= params['epsilon'] <= 1 and 0 <= params['alpha'] <= 1 and 0 <= params['gamma'] <= 1 and params['episodes'] > 0):
                messagebox.showerror("Lỗi tham số", "Giá trị tham số không hợp lệ.", parent=self.root)
                return None
            return params
        except ValueError:
            messagebox.showerror("Lỗi tham số", "Vui lòng nhập số hợp lệ.", parent=self.root)
            return None


    def q_learning_solve(self):
        self.update_status("Bắt đầu Q-Learning...")
        q_params = self.get_q_learning_params()
        if not q_params:
            self.update_status("Q-Learning bị hủy do thiếu tham số.")
            return None, 0

        episodes = q_params['episodes']
        epsilon = q_params['epsilon'] 
        alpha = q_params['alpha']     
        gamma = q_params['gamma']     

        
        action_deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)] # U, D, L, R
        num_actions = len(action_deltas)
        q_table = {} 

        max_steps_per_episode = 75 

        for episode_num in range(episodes):
            if self.check_stop_condition(episode_num, max(1, episodes // 100)): break 

            current_state_np = self.start_state.copy() 
            current_state_tuple = self.state_to_tuple(current_state_np)
            
            if current_state_tuple not in q_table:
                q_table[current_state_tuple] = [0.0] * num_actions

            for step in range(max_steps_per_episode):
                if self.stop_flag: break

                
                if random.random() < epsilon:
                    action_index = random.randrange(num_actions) 
                else:
                    
                    max_q = -float('inf')
                    best_actions = []
                    for i in range(num_actions):
                        q_val = q_table[current_state_tuple][i]
                        if q_val > max_q:
                            max_q = q_val
                            best_actions = [i]
                        elif q_val == max_q:
                            best_actions.append(i)
                    action_index = random.choice(best_actions) if best_actions else random.randrange(num_actions)


                move_delta = action_deltas[action_index]
                next_state_np = self.apply_move(current_state_np, move_delta)

                reward = 0
                next_state_tuple = None

                if next_state_np is None: 
                    reward = -10 
                    next_state_tuple = current_state_tuple 
                else:
                    next_state_tuple = self.state_to_tuple(next_state_np)
                    if next_state_tuple not in q_table: 
                        q_table[next_state_tuple] = [0.0] * num_actions

                    if np.array_equal(next_state_np, self.goal_state):
                        reward = 100 
                    else:
                        
                        reward = -(self.get_selected_heuristic(next_state_np)) / 10.0 
                        

                
                old_q_value = q_table[current_state_tuple][action_index]
                next_max_q = max(q_table[next_state_tuple]) 
                new_q_value = old_q_value + alpha * (reward + gamma * next_max_q - old_q_value)
                q_table[current_state_tuple][action_index] = new_q_value

                current_state_np = next_state_np if next_state_np is not None else current_state_np
                current_state_tuple = self.state_to_tuple(current_state_np) 

                if reward == 100: 
                    break
            if self.stop_flag: break
        

        if self.stop_flag:
            self.update_status(f"Q-Learning dừng sau {episode_num + 1} episodes.")
            return None, episode_num + 1

        
        path_from_q_table = [self.start_state.tolist()]
        current_eval_state_np = self.start_state.copy()
        max_path_steps = 50 
        for _ in range(max_path_steps):
            current_eval_tuple = self.state_to_tuple(current_eval_state_np)
            if current_eval_tuple not in q_table: 
                self.update_status("Q-Learning: Không thể tìm đường đi, trạng thái chưa được học.")
                
                break 
            q_values_for_state = q_table[current_eval_tuple]
            best_action_idx = q_values_for_state.index(max(q_values_for_state)) 

            next_eval_state_np = self.apply_move(current_eval_state_np, action_deltas[best_action_idx])

            if next_eval_state_np is None: 
                self.update_status("Q-Learning: Bị kẹt khi tìm đường đi từ Q-table.")
                
                break
            path_from_q_table.append(next_eval_state_np.tolist())
            current_eval_state_np = next_eval_state_np

            if np.array_equal(current_eval_state_np, self.goal_state):
                break 
        else: 
            if not np.array_equal(current_eval_state_np, self.goal_state):
                 self.update_status(f"Q-Learning: Không tìm thấy đích từ Q-table sau {max_path_steps} bước.")
                 

        if np.array_equal(np.array(path_from_q_table[-1]), self.goal_state):
            self.update_status(f"Q-Learning: Huấn luyện hoàn tất ({episodes} episodes). Đường đi được suy ra.")
            return path_from_q_table, episodes
        else:
            self.update_status(f"Q-Learning: Huấn luyện hoàn tất. Không tìm thấy đích từ Q-table.")
            messagebox.showinfo("Q-Learning", f"Hoàn thành {episodes} episodes.\nKhông thể suy ra đường đi tới đích từ Q-table đã học.")

            if len(path_from_q_table) > 1:
                self.display_solution_path(path_from_q_table[1:]) 
                self.animate_solution(path_from_q_table)
            return None, episodes


    def animate_solution(self, solution_path_states): 
        if not solution_path_states or not isinstance(solution_path_states, list):
             self.update_grid(self.start_grid, self.start_state) 
             self.root.update()
             return

        if not solution_path_states:
            return

        num_steps_to_animate = len(solution_path_states) -1
        if num_steps_to_animate < 0 : num_steps_to_animate = 0

        self.update_status(f"Bắt đầu hoạt ảnh ({num_steps_to_animate} bước)...")
        # First state in solution_path_states is the actual start
        self.update_grid(self.start_grid, np.array(solution_path_states[0]))
        self.root.update()
        if num_steps_to_animate > 0 : time.sleep(self.animation_speed)


        for i in range(1, len(solution_path_states)): 
             state_list = solution_path_states[i]
             if self.stop_flag:
                 self.update_status(f"Hoạt ảnh dừng ở bước {i}.")
                 self.update_grid(self.start_grid, np.array(state_list))
                 self.root.update()
                 break

             state_arr = np.array(state_list)
             self.update_grid(self.start_grid, state_arr)
             self.update_status(f"Hoạt ảnh: Bước {i}/{num_steps_to_animate}")
             self.root.update()
             time.sleep(self.animation_speed)

        if not self.stop_flag:
             self.update_grid(self.start_grid, np.array(solution_path_states[-1]))
             self.update_status(f"Hoạt ảnh hoàn thành ({num_steps_to_animate} bước).")
             self.root.update()


    def update_grid(self, grid_labels, state_array_data):
        if not grid_labels or len(grid_labels) != 3 or not all(len(row) == 3 for row in grid_labels):
             return
        try:
            state_array = np.array(state_array_data) # Ensure numpy
            if state_array.shape != (3,3): return

            for i in range(3):
                for j in range(3):
                    cell_label = grid_labels[i][j]
                    if isinstance(cell_label, tk.Widget) and cell_label.winfo_exists():
                        val = state_array[i, j]
                        text = str(val) if val != 0 else ""
                        bg_color = "lightgrey" if val != 0 else "white"
                        cell_label.config(text=text, bg=bg_color)
        except Exception:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = Puzzle8App(root)
    root.mainloop()
