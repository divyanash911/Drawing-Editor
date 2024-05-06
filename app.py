import tkinter as tk
from tkinter import simpledialog

class DrawingEditor:
    def __init__(self, master):

        self.current_items = set()

        self.master = master
        master.title("Drawing Editor")

        self.canvas = tk.Canvas(master, width=800, height=800, bg="white")
        self.canvas.pack()

        self.width = self.canvas.winfo_width()
        self.height = self.canvas.winfo_height()
        self.centre_x = self.width / 2
        self.centre_y = self.height / 2

        self.draw_button = tk.Menubutton(master, text="Draw", relief="raised")
        self.draw_button.pack(side=tk.LEFT)
        self.draw_button.menu = tk.Menu(self.draw_button, tearoff=0)
        self.draw_button["menu"] = self.draw_button.menu

        # Add options to the dropdown menu
        self.draw_button.menu.add_command(label="Line", command=self.start_draw_line)
        self.draw_button.menu.add_command(label="Rectangle", command=self.start_draw_rectangle)

        self.select_button = tk.Button(master, text="Select", command=self.start_select)
        self.select_button.pack(side=tk.LEFT)

        self.save_ascii_button = tk.Button(master, text="Save as ASCII", command=self.save_ascii)
        self.save_ascii_button.pack(side=tk.RIGHT)

        self.save_xml_button = tk.Button(master, text="Save as XML", command=self.save_xml)
        self.save_xml_button.pack(side=tk.RIGHT)

        self.open_xml_button = tk.Button(master,text="Open",command=self.open_xml)
        self.open_xml_button.pack(side=tk.RIGHT)


        self.selected_objects = set()
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.selection_rectangle = None
        self.select_mode = False
        self.current_shape = None
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.group_button = None
        self.edit_button = None
        self.ungrp_button = None

        self.item_state = {}
        self.selected_objects = set()  # Declaration of selected_objects
        self.group_items = {}


    def open_xml(self):

        self.canvas.delete("all")

        file=simpledialog.askstring(title='Open',prompt="Enter file name: ",parent=self.master)
        f_name = file
        if not file or (file.find(".xml") == -1 and file.find(".txt")==-1) :
            simpledialog.messagebox.showinfo("Error", "Invalid file name")
            return
        file = open(file, "r")
        
        if f_name.find(".xml") != -1:
            for line in file:
                if line.startswith("<line>"):
                    begin = line[line.index("<begin>") + 7:line.index("</begin>")].split(",")
                    end = line[line.index("<end>") + 5:line.index("</end>")].split(",")
                    color = line[line.index("<color>") + 7:line.index("</color>")]
                    shape = self.canvas.create_line(begin[0], begin[1], end[0], end[1], fill=color)
                    self.item_state[shape] = color
                    self.current_items.add(shape)
                elif line.startswith("<rectangle>"):
                    upper_left = line[line.index("<upper_left>") + 12:line.index("</upper_left>")].split(",")
                    lower_right = line[line.index("<lower_right>") + 13:line.index("</lower_right>")].split(",")
                    color = line[line.index("<color>") + 7:line.index("</color>")]
                    style = line[line.index("<style>") + 7:line.index("</style>")]
                    if style == "rounded":
                        shape = self.canvas.create_rectangle(upper_left[0], upper_left[1], lower_right[0], lower_right[1], outline=color,dash=(4,4))
                    elif style == "sharp":   
                        shape = self.canvas.create_rectangle(upper_left[0], upper_left[1], lower_right[0], lower_right[1], outline=color)
                    self.item_state[shape] = color
                    self.current_items.add(shape)
                

        elif f_name.find(".txt") != -1:
            for line in file:
                if line.startswith("Line"):
                    line = line.split(" ")
                    # print(line[2])
                    coords = line[1].split(",")
                    line[2]=line[2].replace("\n","")
                    shape = self.canvas.create_line(coords[0], coords[1], coords[2], coords[3], fill=line[2])
                    self.item_state[shape] = line[2]
                    self.current_items.add(shape)
                elif line.startswith("Rectangle"):
                    line = line.split(" ")
                    line[2]=line[2].replace("\n","")
                    coords = line[1].split(",")
                    style = line[3]
                    if style == "rounded":
                        shape = self.canvas.create_rectangle(coords[0], coords[1], coords[2], coords[3], outline=line[2],dash=(4,4))
                    elif style == "sharp":
                        shape = self.canvas.create_rectangle(coords[0], coords[1], coords[2], coords[3], outline=line[2])
                    self.item_state[shape] = line[2]
                    self.current_items.add(shape)
        
        file.close()

    def getdash(self,item):
        if self.canvas.itemcget(item,"dash") == (4,4):
            return "rounded"
        else:
            return "sharp"

    def save_ascii(self):

        output_string = ""
        op_file_name = simpledialog.askstring(title='Save',prompt="Enter file name: ",parent=self.master)
        if not op_file_name or op_file_name.index(".txt") == -1:
            simpledialog.messagebox.showinfo("Error", "Invalid file name")
            return
        op_file = open(op_file_name, "w")
        for item in self.current_items:
            if self.canvas.type(item).lower() == "line":
                output_string += f"line {self.canvas.coords(item)[0]},{self.canvas.coords(item)[1]},{self.canvas.coords(item)[2]},{self.canvas.coords(item)[3]} {self.canvas.itemcget(item,"fill")}\n"
            elif self.canvas.type(item).lower() == "rectangle":
                output_string += f"rectangle {self.canvas.coords(item)[0]},{self.canvas.coords(item)[1]},{self.canvas.coords(item)[2]},{self.canvas.coords(item)[3]} {self.canvas.itemcget(item,"outline")} {self.getdash(item)}\n"
        if output_string == "":
            output_string = "No items to save"
        else:
            op_file.write(output_string)
            simpledialog.messagebox.showinfo("Success", f"Items saved to {op_file_name}")


        pass
    def save_xml(self):

        output_string = ""
        op_file_name = simpledialog.askstring(title='Save',prompt="Enter file name: ",parent=self.master)
        if not op_file_name or op_file_name.index(".xml") == -1:
            simpledialog.messagebox.showinfo("Error", "Invalid file name")
            return
        op_file = open(op_file_name, "w")
        for item in self.current_items:
            if self.canvas.type(item).lower() == "line":
                output_string += f"<line><begin>{self.canvas.coords(item)[0]},{self.canvas.coords(item)[1]}</begin><end>{self.canvas.coords(item)[2]},{self.canvas.coords(item)[3]}</end><color>{self.canvas.itemcget(item,'fill')}</color></line>\n"
            elif self.canvas.type(item).lower() == "rectangle":
                output_string += f"<rectangle><upper_left>{self.canvas.coords(item)[0]},{self.canvas.coords(item)[1]}</upper_left><lower_right>{self.canvas.coords(item)[2]},{self.canvas.coords(item)[3]}</lower_right><color>{self.canvas.itemcget(item,'outline')}</color><style>{self.getdash(item)}</style></rectangle>\n"
        if output_string == "":
            output_string = "No items to save"
        else:
            op_file.write(output_string)
            simpledialog.messagebox.showinfo("Success", f"Items saved to {op_file_name}")


        pass        

    def start_draw_line(self):
        self.reset_draw_mode()
        self.canvas.bind("<Button-1>", self.on_click_line)

    def on_click_line(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.canvas.bind("<B1-Motion>", self.draw_temp_line)
        self.canvas.bind("<ButtonRelease-1>", self.draw_final_line)

    def draw_temp_line(self, event):
        if self.selection_rectangle:
            self.canvas.delete(self.selection_rectangle)
        if self.current_shape:
            self.canvas.delete(self.current_shape)
        self.current_shape = self.canvas.create_line(self.start_x, self.start_y, event.x, event.y, fill="black")

    def draw_final_line(self, event):
        # self.current_items.add(self.current_shape)
        if self.current_shape:
            self.canvas.delete(self.current_shape)
        shape = self.canvas.create_line(self.start_x, self.start_y, event.x, event.y, fill="black")
        
        self.item_state[tuple(self.canvas.coords(shape))] = "black"
        self.current_items.add(shape)
        self.reset_draw_mode()

    def start_draw_rectangle(self):
        self.reset_draw_mode()
        self.canvas.bind("<Button-1>", self.on_click_rect)

    def on_click_rect(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.canvas.bind("<B1-Motion>", self.draw_temp_rect)
        self.canvas.bind("<ButtonRelease-1>", self.draw_final_rect)

    def draw_temp_rect(self, event):
        if self.selection_rectangle:
            self.canvas.delete(self.selection_rectangle)
        if self.current_shape:
            self.canvas.delete(self.current_shape)
        self.current_shape = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="black")

    def draw_final_rect(self, event):
        # self.current_items.add(self.current_shape)
        if self.current_shape:
            self.canvas.delete(self.current_shape)
        shape=self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="black")
        
        self.item_state[tuple(self.canvas.coords(shape))] = "black"
        self.current_items.add(shape)
        self.reset_draw_mode()

    def start_select(self):
        self.reset_draw_mode()
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.select_mode = True

    def remove_menu(self):
        if self.del_button:
            self.del_button.destroy() #remove selection menu
        if self.copy_button:
            self.copy_button.destroy()
        if self.move_button:
            self.move_button.destroy()
        if self.edit_button:
            self.edit_button.destroy()
        if self.group_button:
            self.group_button.destroy()
        if self.ungrp_button:
            self.ungrp_button.destroy()

        self.selected_objects.clear()


    def on_click(self, event):
        if self.select_mode:
            self.start_x = event.x
            self.start_y = event.y
            if self.selection_rectangle:
                self.canvas.delete(self.selection_rectangle)
            self.selection_rectangle = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="black")
        elif not self.select_mode:
            for item in self.selected_objects:
                # print(self.item_state)
                try:
                        if tuple(self.canvas.coords(item)) in self.item_state:
                            self.canvas.itemconfig(item, outline=self.item_state[tuple(self.canvas.coords(item))], width=2)
                except:
                        if tuple(self.canvas.coords(item)) in self.item_state:
                            self.canvas.itemconfig(item, fill=self.item_state[tuple(self.canvas.coords(item))], width=2)
                        
            
            self.remove_menu()

            self.selected_objects.clear()

    def start_delete(self):
        for item in self.selected_objects:
            self.canvas.delete(item)
            try:    
                self.current_items.remove(item)
            except:
                pass
        
        self.selected_objects.clear()
        self.del_button.destroy()
        self.remove_menu()

    def start_copy(self):

        self.reset_draw_mode()
        self.canvas.bind("<Button-1>", self.on_click_copy)

    def updated_coords(self,coords):
        for i in range(0, len(coords)):
            if i % 2 == 0:
                coords[i] = coords[i] -self.centre_x + self.start_x
            else:
                coords[i] = coords[i] -  self.centre_y + self.start_y

        return coords
    
    def on_click_copy(self, event):
        self.start_x = event.x
        self.start_y = event.y

        for item in self.selected_objects:
            if self.canvas.type(item) == "line":
                self.current_shape = self.canvas.create_line(self.updated_coords(self.canvas.coords(item)), fill="black")
            elif self.canvas.type(item) == "rectangle":
                self.current_shape = self.canvas.create_rectangle(self.updated_coords(self.canvas.coords(item)), outline="black")

        self.reset_draw_mode()
        self.remove_menu()

    def start_move(self):
        self.reset_draw_mode()
        self.canvas.bind("<Button-1>", self.on_click_move)

    def on_click_move(self, event):

        self.start_x = event.x
        self.start_y = event.y

        for item in self.selected_objects:
            if self.canvas.type(item) == "line":
                self.current_shape = self.canvas.create_line(self.updated_coords(self.canvas.coords(item)), fill="black")
            elif self.canvas.type(item) == "rectangle":
                self.current_shape = self.canvas.create_rectangle(self.updated_coords(self.canvas.coords(item)), outline="black")


            self.canvas.delete(item)
        
        self.reset_draw_mode()
        self.remove_menu()
        

    def on_drag(self, event):
        if self.select_mode:
            if self.selection_rectangle:
                self.canvas.delete(self.selection_rectangle)
            self.end_x = event.x
            self.end_y = event.y
            self.selection_rectangle = self.canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y, outline="black",dash=(4,4))

    def start_edit(self):

        for item in self.selected_objects:
            if self.canvas.type(item) == "line":
                # while True:
                new_inp = simpledialog.askstring(title='Edit',prompt="Enter new color(Red,Blue,Green,Yellow): ",parent=self.master)
                new_inp=new_inp.lower()
                if new_inp == "red" or new_inp == "blue" or new_inp == "green" or new_inp == "yellow":
                    self.canvas.itemconfig(item, fill=new_inp)
                    self.item_state[tuple(self.canvas.coords(item))]=new_inp
                        
                else:
                    simpledialog.messagebox.showinfo("Error", "Invalid color")
                    
            elif self.canvas.type(item) == "rectangle":

                new_inp = simpledialog.askstring(title='Edit',prompt="Enter change type?(Color or style): ",parent=self.master)

                if new_inp.lower() == "color":
                    new_inp = simpledialog.askstring(title='Edit',prompt="Enter new color(Red,Blue,Green,Yellow): ",parent=self.master)
                    new_inp = new_inp.lower()
                    if new_inp == "red" or new_inp == "blue" or new_inp == "green" or new_inp == "yellow":
                        self.canvas.itemconfig(item, outline=new_inp)
                        self.item_state[tuple(self.canvas.coords(item))]=new_inp
                    else:
                        simpledialog.messagebox.showinfo("Error", "Invalid color")
                elif new_inp.lower() == "style":
                    # new_inp.destroy()
                    new_inp = simpledialog.askstring(title='Edit',prompt="Enter new style(sharp or rounded corners): ",parent=self.master)
                    if new_inp == "rounded":
                        self.canvas.itemconfig(item,outline="black",dash=(4,4))
                    elif new_inp == "sharp":
                        self.canvas.itemconfig(item, outline="black")
                    else:
                        simpledialog.messagebox.showinfo("Error", "Invalid style")
        
        self.remove_menu()
        self.selected_objects =  set()

    def start_group(self):

        selected_items = list(self.selected_objects)
        if len(selected_items) < 2:
            return

        group_id = self.create_group(selected_items)

        for item in selected_items:
            self.group_items[item] = group_id


        pass

    def create_group(self, selected_items):
        #create bounding box

        min_x = self.width
        min_y = self.height
        max_x = 0
        max_y = 0

        for item in selected_items:
            if item:
                coords = self.canvas.coords(item)
                if coords:
                    min_x = min(min_x, coords[0], coords[2])
                    min_y = min(min_y, coords[1], coords[3])
                    max_x = max(max_x, coords[0], coords[2])
                    max_y = max(max_y, coords[1], coords[3])

        group_id = tuple((min_x, min_y, max_x, max_y))
        return group_id


    def on_release(self, event):
        if self.select_mode:  
            selected_items = self.canvas.find_overlapping(self.start_x, self.start_y, self.end_x, self.end_y)

            neighbour = []
            flag=0
            for item in selected_items:
                gp_id = self.group_items.get(item)
                if gp_id:
                    for neighbours in self.group_items:
                        if self.group_items[neighbours] == gp_id and neighbours!=item:
                            neighbour.append(neighbours)
                            flag=1
            
            selected_items = selected_items + tuple(neighbour)           

        # Update selected_objects set
            for item in selected_items:
                if item not in self.selected_objects:
                    self.selected_objects.add(item)
                    try:
                        self.canvas.itemconfig(item, outline="red", width=2)
                    except:
                        self.canvas.itemconfig(item, fill="red", width=2)

            if flag==1:
                self.ungrp_button = tk.Button(self.master, text="Ungroup", command=self.start_ungroup)
                self.ungrp_button.pack(side=tk.LEFT)


            # for item in selected_items:
            #     if item not in self.selected_objects:
            #         self.selected_objects.add(item)
            #         try:
            #             self.canvas.itemconfig(item, outline="red", width=2)
            #         except:
            #             self.canvas.itemconfig(item, fill="red", width=2)

            if len(self.selected_objects) > 1:
                self.del_button = tk.Button(self.master, text="Delete", command=self.start_delete)
                self.del_button.pack(side=tk.LEFT)
                self.copy_button = tk.Button(self.master, text="Copy", command=self.start_copy)
                self.copy_button.pack(side=tk.LEFT)
                self.move_button = tk.Button(self.master, text="Move", command=self.start_move)
                self.move_button.pack(side=tk.LEFT)

                if len(self.selected_objects) == 2:
                    self.edit_button = tk.Button(self.master, text="Edit", command=self.start_edit)
                    self.edit_button.pack(side=tk.LEFT)
                else:
                    
                    self.group_button = tk.Button(self.master, text="Group", command=self.start_group)
                    self.group_button.pack(side=tk.LEFT)

                self.centre_x = (self.start_x + self.end_x) / 2
                self.centre_y = (self.start_y + self.end_y) / 2

            self.canvas.delete(self.selection_rectangle)
            self.select_mode = False

    def start_ungroup(self):
        for item in self.selected_objects:
            if item in self.group_items:
                del self.group_items[item]
                self.selected_objects.remove(item)
            try:
                if tuple(self.canvas.coords(item)) in self.item_state:
                    self.canvas.itemconfig(item, outline=self.item_state[tuple(self.canvas.coords(item))], width=2)
            except:
                if tuple(self.canvas.coords(item)) in self.item_state:
                    self.canvas.itemconfig(item, fill=self.item_state[tuple(self.canvas.coords(item))], width=2)
                
        self.ungrp_button.destroy()
        self.remove_menu()

    def reset_draw_mode(self):
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        

def main():
    root = tk.Tk()
    drawing_editor = DrawingEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
