import os
import cv2
import numpy
import datetime
import pyautogui
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk

SelectedFile = '' # 選択された画像の絶対パス
ImageScale = 1.0 # 表示されている画像のサイズの倍率
WindowSizeWidth = 0 # ウィンドウの横のサイズ
WindowSizeHeight = 0 # ウィンドウの縦のサイズ
TrimmingImg_x1 = None # トリミングする画像の始点x
TrimmingImg_y1 = None # トリミングする画像の始点y
TrimmingImg_x2 = None # トリミングする画像の終点x
TrimmingImg_y2 = None # トリミングする画像の終点y
SaveImageFolder = '' # 画像の保存先

class Trimming():

    def __init__(self):

        root = tk.Tk()
        root.title('Trimming Application')
        root.state('zoomed')
        # root.resizable(width = False, height = False)

        self.View(root)

        root.mainloop()

    def View(self, root): # 外観の設定

        global WindowSizeWidth
        global WindowSizeHeight
        WindowSizeWidth =  root.winfo_screenwidth()
        WindowSizeHeight = root.winfo_screenheight()

        
        frame_display = tk.Frame(root, width = WindowSizeWidth, height = WindowSizeHeight - 150, bg = '#cccccc')
        frame_display.pack()

        frame_other = tk.Frame(root)
        frame_other.pack(side = 'bottom', pady = 15)

        button_getImg = tk.Button(frame_other, text = '画像を選択する',  width = 50, height = 3)
        button_getImg.bind('<ButtonPress>', lambda event, arg = frame_display: self.file_dialog(event, arg)) # クリックイベント
        button_getImg.pack(side = 'left')

        button_saveFolder = tk.Button(frame_other, text = '保存先',  width = 20, height = 3)
        button_saveFolder.bind('<ButtonPress>',  self.folder_dialog) # クリックイベント
        button_saveFolder.pack(side = 'left')

        self.file_name = tk.StringVar() # ファイルの選択状況をテキスト化
        self.file_name.set('ファイル名:未選択です')
        label_file = tk.Label(frame_other, textvariable = self.file_name)
        label_file.pack(side = 'top')

        self.folder_name = tk.StringVar()
        self.folder_name.set('保存先:未定です')
        label_folder = tk.Label(frame_other, textvariable = self.folder_name)
        label_folder.pack(side = 'bottom')

    def file_dialog(self, event, frame): # ファイルダイアログの設定

        global SelectedFile # 選択ファイルを初期化

        tmpFile = SelectedFile
        
        fTyp = [('PNG Files', '*.png'), ('JPG Files', '*.jpg'), ('JPEG Files', '*.jpeg')]
        iDir = os.path.abspath(os.path.dirname(__file__))
        SelectedFile = tk.filedialog.askopenfilename(filetypes = fTyp, initialdir = iDir)

        if len(SelectedFile) == 0:
            if len(tmpFile) == 0:
                self.file_name.set('選択をキャンセルしました')
            else:
                SelectedFile = tmpFile
        else: # ファイルの選択をした場合
            self.file_name.set(f'ファイル名:{SelectedFile.split("/")[-1]}')
            self.Destroy(frame) 
            self.Display(frame)
    
    def folder_dialog(self, event):
        global SaveImageFolder

        iDir = os.getcwd()
        SaveImageFolder = tk.filedialog.askdirectory(initialdir = iDir)
        if len(SaveImageFolder) != 0:
            self.folder_name.set(f'保存先:{SaveImageFolder}')
    
    def Display(self, frame): # 指定された画像の表示

        OrgImg = Image.open(SelectedFile)
        img = OrgImg.copy()

        img = self.Resize(img)

        canvas = tk.Canvas(frame, width = img.width, height = img.height)
        canvas.pack()
        
        self.tkimg = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, image = self.tkimg, anchor = 'nw', tag = 'image')

        self.MouseEvents(canvas)
    
    def Destroy(self, frame): # 前に選択された写真を消去

        children = frame.winfo_children()
        for child in children:
            child.destroy()
    
    def Resize(self, img): # 画像のサイズを変更

        global ImageScale

        if(img.width > WindowSizeWidth and img.height > WindowSizeHeight - 150): # 縦と横のどちらもはみ出した場合
            if(WindowSizeWidth / img.width >= (WindowSizeHeight - 150) / img.height):
                ImageScale = ((WindowSizeHeight - 150) / img.height)
                img = img.resize((int(img.width * ((WindowSizeHeight - 150) / img.height)), int(img.height * ((WindowSizeHeight - 150) / img.height))))
            else:
                ImageScale = (WindowSizeWidth / img.width)
                img = img.resize((int(img.width * (WindowSizeWidth / img.width)), int(img.height * (WindowSizeWidth / img.width))))
        elif(img.width > WindowSizeWidth): # 横のみはみ出した場合
            ImageScale = (WindowSizeWidth / img.width)
            img = img.resize((int(img.width * (WindowSizeWidth / img.width)), int(img.height * (WindowSizeWidth / img.width))))
        elif(img.height > WindowSizeHeight - 150): # 縦のみはみ出した場合
            ImageScale = (WindowSizeHeight - 150) / img.height
            img = img.resize((int(img.width * ((WindowSizeHeight - 150) / img.height)), int(img.height * ((WindowSizeHeight - 150) / img.height))))
        
        return img

    def MouseEvents(self, canvas): # マウスイベント

        canvas.bind('<Button-1>', self.leftClick) 
        canvas.bind('<B1-Motion>', lambda event, arg = canvas: self.leftMotion(event, arg)) 
        canvas.bind('<ButtonRelease-1>', lambda event, arg = canvas: self.leftRelease(event, arg))

    def leftClick(self, event): # 左クリックされたとき
        global SaveImageFolder

        while len(SaveImageFolder) == 0:
            messagebox.showwarning('注意', '画像の保存場所を指定してください')
            self.folder_dialog(event)

        global TrimmingImg_x1
        global TrimmingImg_y1
        TrimmingImg_x1 = event.x
        TrimmingImg_y1 = event.y
        print(f'x1:{TrimmingImg_x1}, y1:{TrimmingImg_y1}')

    def leftMotion(self, event, canvas): # 左クリック状態からドラッグされたとき
        
        self.deleteRectangle(canvas)
        self.createRectangle(event, canvas)
    
    def leftRelease(self, event, canvas): # 左クリックが離されたとき

        global TrimmingImg_x2
        global TrimmingImg_y2
        TrimmingImg_x2 = event.x
        TrimmingImg_y2 = event.y
        print(f'x2:{TrimmingImg_x2}, y2:{TrimmingImg_y2}')

        if len(SaveImageFolder) != 0:
            self.SaveImage(canvas)
    
    def SaveImage(self, canvas):

        res = messagebox.askokcancel('確認', '指定した部分を保存しますか？')

        self.deleteRectangle(canvas)

        if res:
            
            global TrimmingImg_x1
            global TrimmingImg_y1
            global TrimmingImg_x2
            global TrimmingImg_y2

            x, y = None, None
            w, h = None, None
            
            if (TrimmingImg_x2 - TrimmingImg_x1 >= 0 and TrimmingImg_y2 - TrimmingImg_y1 >= 0):
                x = TrimmingImg_x1
                y = TrimmingImg_y1
                w = TrimmingImg_x2 - TrimmingImg_x1
                h = TrimmingImg_y2 - TrimmingImg_y1

            elif (TrimmingImg_x2 - TrimmingImg_x1 < 0 and TrimmingImg_y2 - TrimmingImg_y1 < 0):
                x = TrimmingImg_x2
                y = TrimmingImg_y2
                w = TrimmingImg_x1 - TrimmingImg_x2
                h = TrimmingImg_y1 - TrimmingImg_y2

            elif (TrimmingImg_x2 - TrimmingImg_x1 >= 0 and TrimmingImg_y2 - TrimmingImg_y1 < 0):
                x = TrimmingImg_x1
                y = TrimmingImg_y2
                w = TrimmingImg_x2 - TrimmingImg_x1
                h = TrimmingImg_y1 - TrimmingImg_y2

            else:
                x = TrimmingImg_x2
                y = TrimmingImg_y1
                w = TrimmingImg_x1 - TrimmingImg_x2
                h = TrimmingImg_y2 - TrimmingImg_y1

            print(f'x:{x}, y:{y}, w:{w}, h:{h}')
            
            global SelectedFile

            img = cv2.imread(SelectedFile)

            if isinstance(img, numpy.ndarray):
                height, width, channels = img.shape

                img_changeSize = cv2.resize(img, (int(width * ImageScale), int(height * ImageScale))) # 画像サイズの変更

                img_trim = img_changeSize[y:y+h, x:x+w] # トリミング

                dt = datetime.datetime.now()

                cv2.imwrite(f'{SaveImageFolder}/{dt.strftime("%Y%m%d%H%M%S")}_{SelectedFile.split("/")[-1]}', img_trim) # トリミングした画像を保存
            
            else:
                messagebox.showerror('禁止', 'この画像はトリミングが出来ません')
    
    def createRectangle(self, event, canvas):
        canvas.create_rectangle(TrimmingImg_x1, TrimmingImg_y1, event.x, event.y, outline = 'red', width = 3, tag = 'rectangle')
    
    def deleteRectangle(self, canvas):
        objs = canvas.find_withtag('rectangle')
        for obj in objs:
            canvas.delete(obj)

if __name__ == '__main__':
    Trimming()