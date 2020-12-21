
```
# PyQT5将窗口放在屏幕中间例子
def center(self):  
    screen = QDesktopWidget().screenGeometry()  
    size = self.geometry()        
    self.move((screen.width() - size.width()) / 2,  (screen.height() - size.height()) / 2)  
    
# 程序图标例子
def initUI(self):
    self.setGeometry(300,  300,  250,  150)  
    self.setWindowTitle('演示程序图标例子')  
    self.setWindowIcon(QIcon('./images/cartoon1.ico'))

# Button图标
self.btn2 = QPushButton('image')
self.btn2.setIcon(QIcon(QPixmap("./images/python.png")))

# 气泡提示
def initUI(self):
    QToolTip.setFont(QFont('SansSerif', 10))
    self.setToolTip('这是一个<b>气泡提示</b>')
    
# QLineEdit输入检测
e1 = QLineEdit()
e1.setValidator( QIntValidator() )

# 读取输入框值
self.sp = QSpinBox()
"current value:" + str(self.sp.value())

# QDialog 例子
self.btn = QPushButton()
self.btn.clicked.connect(self.showdialog)
def showdialog(self ):
    dialog = QDialog()
    btn = QPushButton("ok", dialog )
    btn.move(50,50)
    dialog.setWindowTitle("Dialog")
    dialog.setWindowModality(Qt.ApplicationModal)
    dialog.exec_()

# 警告对话框    16384:退出, 65536:取消
self.myButton = QPushButton(self)
self.myButton.clicked.connect(self.msg)
def msg(self):
    QMessageBox.information(self, "标题", "对话框消息正文", QMessageBox.Yes | QMessageBox.No ,  QMessageBox.Yes ) 

```
