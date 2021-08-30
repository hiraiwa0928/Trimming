import os
import cv2
import glob
import time
import natsort
import datetime
import pyautogui
import subprocess
import numpy as np
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
from os import listdir

files = [] # フォルダーの中のファイル
index = None # filesの一番最初の画像ファイルの場所
SelectedFile = '' # 選択された画像の絶対パス
SelectedFolder_Save = '' # 画像の保存先
SaveFileNum = 0 # 保存された画像の枚数
SelectedFolder_AllImage = '' # トリミングする対象のフォルダー
ImageScale = 1.0 # 表示されている画像のサイズの倍率
WindowSizeWidth = 0 # ウィンドウの横のサイズ
WindowSizeHeight = 0 # ウィンドウの縦のサイズ
TrimmingImg_x1 = None # トリミングする画像の始点x
TrimmingImg_y1 = None # トリミングする画像の始点y
TrimmingImg_x2 = None # トリミングする画像の終点x
TrimmingImg_y2 = None # トリミングする画像の終点y
BottomSpace = 250 # ボタンの配置するスペースの確保
x = None # トリミングする範囲ｘ
y = None # トリミングする範囲ｙ
w = None # トリミングする範囲ｗ
h = None # トリミングする範囲ｈ

class Trimming():

    def __init__(self):

        root = tk.Tk()
        root.title('Trimming Application')
        root.state('zoomed')

        self.View(root)

        root.mainloop()

    def View(self, root): # 外観の設定

        global WindowSizeWidth
        global WindowSizeHeight
        WindowSizeWidth =  root.winfo_screenwidth()
        WindowSizeHeight = root.winfo_screenheight()

        
        frame_display = tk.Frame(root, width = WindowSizeWidth, height = WindowSizeHeight - BottomSpace, bg = '#cccccc')
        frame_display.pack()

        frame_other = tk.Frame(root)
        frame_other.pack(pady = 30)

        button_getImg = tk.Button(frame_other, text = '指定した画像をトリミング',  width = 50, height = 3)
        button_getImg.bind('<ButtonPress>', lambda event, arg = frame_display: self.file_dialog(event, arg)) # クリックイベント
        button_getImg.pack(side = 'left')

        button_trimmingAllFile = tk.Button(frame_other, text = 'フォルダー内のすべての画像をトリミング',  width = 50, height = 3)
        button_trimmingAllFile.bind('<ButtonPress>', lambda event, arg = frame_display: self.Trimming_AllFile(event, arg)) # クリックイベント
        button_trimmingAllFile.pack(side = 'left')

        button_saveFolder = tk.Button(frame_other, text = '保存先',  width = 20, height = 3)
        button_saveFolder.bind('<ButtonPress>', lambda event, arg = 1: self.folder_dialog(event, arg)) # クリックイベント
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
        if len(SelectedFile) == 0:
            iDir = os.path.abspath(os.path.dirname(__file__))
        else:
            iDir = SelectedFile
        SelectedFile = tk.filedialog.askopenfilename(filetypes = fTyp, initialdir = iDir)

        if len(SelectedFile) == 0:
            if len(tmpFile) == 0:
                self.file_name.set('選択をキャンセルしました')
            else:
                SelectedFile = tmpFile
        else: # ファイルの選択をした場合
            self.file_name.set(f'ファイル名:{SelectedFile.split("/")[-1]}')
            self.Destroy(frame) 
            self.Display(frame, 1)
    
    def folder_dialog(self, event, num): # フォルダダイアログの設定
        
        global SelectedFolder_Save
        global SelectedFolder_AllImage

        if len(SelectedFolder_Save) == 0:
            iDir = os.getcwd()
        else:
            iDir = SelectedFolder_Save
        
        if num == 1:
            SelectedFolder_Save = tk.filedialog.askdirectory(initialdir = iDir)
        else:
            SelectedFolder_AllImage = tk.filedialog.askdirectory(initialdir = iDir)

        if len(SelectedFolder_Save) != 0 and num == 1:
            self.folder_name.set(f'保存先:{SelectedFolder_Save}')
    
    def Display(self, frame, num): # 指定された画像の表示

        OrgImg = Image.open(SelectedFile)
        
        img = OrgImg.copy()

        img = self.Resize(img)

        canvas = tk.Canvas(frame, width = img.width, height = img.height)
        canvas.pack()
        
        self.tkimg = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, image = self.tkimg, anchor = 'nw', tag = 'image')

        self.MouseEvents(canvas, num)
    
    def Destroy(self, frame): # 前に選択された写真を消去

        children = frame.winfo_children()
        for child in children:
            child.destroy()
    
    def Resize(self, img): # 画像のサイズを変更

        global ImageScale

        ImageScale = 1.0

        if(img.width > WindowSizeWidth and img.height > WindowSizeHeight - BottomSpace): # 縦と横のどちらもはみ出した場合
            if(WindowSizeWidth / img.width >= (WindowSizeHeight - BottomSpace) / img.height):
                ImageScale = ((WindowSizeHeight - BottomSpace) / img.height)
                img = img.resize((int(img.width * ((WindowSizeHeight - BottomSpace) / img.height)), int(img.height * ((WindowSizeHeight - BottomSpace) / img.height))))
            else:
                ImageScale = (WindowSizeWidth / img.width)
                img = img.resize((int(img.width * (WindowSizeWidth / img.width)), int(img.height * (WindowSizeWidth / img.width))))
        elif(img.width > WindowSizeWidth): # 横のみはみ出した場合
            ImageScale = (WindowSizeWidth / img.width)
            img = img.resize((int(img.width * (WindowSizeWidth / img.width)), int(img.height * (WindowSizeWidth / img.width))))
        elif(img.height > WindowSizeHeight - BottomSpace): # 縦のみはみ出した場合
            ImageScale = (WindowSizeHeight - BottomSpace) / img.height
            img = img.resize((int(img.width * ((WindowSizeHeight - BottomSpace) / img.height)), int(img.height * ((WindowSizeHeight - BottomSpace) / img.height))))
        
        return img

    def MouseEvents(self, canvas, num): # マウスイベント

        canvas.bind('<Button-1>', self.LeftClick) 
        canvas.bind('<B1-Motion>', lambda event, arg = canvas: self.LeftMotion(event, arg)) 
        canvas.bind('<ButtonRelease-1>', lambda event, arg = canvas: self.LeftRelease(event, arg, num))

    def LeftClick(self, event): # 左クリックされたとき
        global SelectedFolder_Save

        while len(SelectedFolder_Save) == 0:
            messagebox.showwarning('注意', '画像の保存場所を指定してください')
            self.folder_dialog(event)

        global TrimmingImg_x1
        global TrimmingImg_y1
        TrimmingImg_x1 = event.x
        TrimmingImg_y1 = event.y
        print(f'x1:{TrimmingImg_x1}, y1:{TrimmingImg_y1}')

    def LeftMotion(self, event, canvas): # 左クリック状態からドラッグされたとき
        
        self.deleteRectangle(canvas)
        self.createRectangle(event, canvas)
    
    def LeftRelease(self, event, canvas, num): # 左クリックが離されたとき

        global TrimmingImg_x2
        global TrimmingImg_y2
        TrimmingImg_x2 = event.x
        TrimmingImg_y2 = event.y
        print(f'x2:{TrimmingImg_x2}, y2:{TrimmingImg_y2}')

        if len(SelectedFolder_Save) != 0:
            self.GetCoordinate(canvas, num)
    
    def GetCoordinate(self, canvas, num): # トリミングする座標を取得

        global x, y, w, h
        
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

        res = messagebox.askokcancel('確認', '指定した部分をトリミングしますか？')

        self.deleteRectangle(canvas)

        if res:
            dt = datetime.datetime.now()
            self.SaveImage(canvas, num, dt)
            global SaveFileNum
            SaveFileNum = 0
            
    def SaveImage(self, canvas, num, dt): # トリミングした画像を保存

        pilIn = Image.open(SelectedFile)
        img = np.array(pilIn)

        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        if num == 1:
            if isinstance(img, np.ndarray):
                height, width, channels = img.shape

                img_changeSize = cv2.resize(img, (int(width * ImageScale), int(height * ImageScale))) # 画像サイズの変更

                img_trim = img_changeSize[y:y+h, x:x+w] # トリミング

                global SaveFileNum
                SaveFileNum = SaveFileNum + 1

                try:
                    cv2.imwrite(f'{SelectedFolder_Save}/{dt.strftime("%Y%m%d%H%M%S")}_file{SaveFileNum}.png', img_trim) # トリミングした画像を保存
                except:
                    pass
            else:
                messagebox.showerror('禁止', 'このファイルは使用出来ません')
        
        else:
            self.GetImage(canvas)
    
    def createRectangle(self, event, canvas): # トリミングする範囲を囲む
        canvas.create_rectangle(TrimmingImg_x1, TrimmingImg_y1, event.x, event.y, outline = 'red', width = 3, tag = 'rectangle')
    
    def deleteRectangle(self, canvas): # トリミングする範囲を削除
        objs = canvas.find_withtag('rectangle')
        for obj in objs:
            canvas.delete(obj)
        
    def Trimming_AllFile(self, event, frame): # フォルダーの画像をすべてトリミングする
        
        messagebox.showinfo('確認', 'トリミングするフォルダーを選択してください')
        self.Destroy(frame)
        self.folder_dialog('', 2)

        if len(SelectedFolder_AllImage) != 0:

            if len(SelectedFolder_Save) == 0:
                messagebox.showinfo('確認', '画像の保存先を選択してください')
                self.folder_dialog('', 1)
            
            if len(SelectedFolder_Save) != 0 and len(SelectedFolder_AllImage) != 0:

                global files
                global index
                global SelectedFile
                
                files = [filename for filename in listdir(SelectedFolder_AllImage) if not filename.startswith('.')] # フォルダーの中身を取得
                files = natsort.natsorted(files, key=lambda y: y.lower())
                print(files)
                index = None
                for i, file in enumerate(files): # ファイルの拡張子を判別
                    ext = file.split('.')[-1].lower()
                    print(f'{i}: {file}')
                    if(ext == 'png' or ext == 'jpg' or ext == 'jpeg' ):
                        index = i
                        break

                if index != None: # フォルダの中に写真があった時の処理
                    SelectedFile = SelectedFolder_AllImage + '/' + files[index]
                    print(SelectedFile)
                    self.Display(frame, 2)
    
    def GetImage(self, canvas): # フォルダの中の画像を一つ一つ処理
        
        global SelectedFile

        dt = datetime.datetime.now()

        for i in range(index, len(files)):
            ext = files[i].split('.')[-1].lower()
            print(f'{i}: {files[i]}')

            if(ext == 'png' or ext == 'jpg' or ext == 'jpeg'):
                time.sleep(0.03)
                SelectedFile = SelectedFolder_AllImage + '/' + files[i]
                self.SaveImage(canvas, 1, dt)
        
        global SaveFileNum
        SaveFileNum = 0
        
        print(SelectedFolder_Save)
        subprocess.Popen(f'start {SelectedFolder_Save}', shell = True)

if __name__ == '__main__':
    Trimming()