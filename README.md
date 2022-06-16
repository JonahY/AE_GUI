# AE_GUI
GUI for AE
## 软件总体设计
### 软件需求概括
声发射数据分析计算可视化软件采用传统的软件开发生命周期的方法，采用自顶向下，逐步求精的结构化的软件设计方法。本软件主要有以下几方面的功能：
1. 声发射数据读取
2. 波形分析
3. 特征筛选
4. 特征可视化
5. 统计学分析
### 需求概述
1. 要求能够分别对两种声发射数据进行读取。
2. 要求能够对波形数据计算时域特征并导出文件。
3. 要求能够对数据进行通道的选择。
4. 要求能够对特征（时间、能量、振幅、持续时间等）进行筛分。
5. 要求能够对波形进行同步压缩小波变换并可视化。
6. 要求能够可视化分析筛选后的特征。
7. 要求能够对特征进行统计分析计算（最大似然统计、概率密度分布统计、互补累积分布统计、等待时间统计等）并导出文件。
8. 要求能够载入应力应变数据并与特征一并可视化。
### 开发环境
本次开发所用的系统是WINDOW 10，基于Python语言与PyQt5框架，使用pyinstaller作为打包工具，初次运行需先安装Microsoft Visual C++运行库。根据实际功能划分为IO模块、波形分析模块以及特征分析模块，后两者既可单独运行，也可相互结合。模块化使得用户能够根据实际需求进行分析，不必拘束于导入全部数据，省时省力。在程序中有足够的注释语句，大大增强了程序的可读性。
### 总体设计
系统整体架构如图：  
<div align=center>
<img src="/MD_figs/系统架构图.png" height="400px">
</div>  
系统详细的模块信息所示：  
<table align=center>
  <tr>
    <td>主模块</td>
  </tr>
  <tr>
    <td>IO模块</td>
    <td>功能简述</td>
  </tr>
  <tr>
    <td>check_device</td>
    <td>根据用户选择切换不同的声发射设备</td>
  </tr>
  <tr>
    <td>check_mode</td>
    <td>根据用户选择切换不同的载入模式</td>
  </tr>
  <tr>
    <td>check_parameter</td>
    <td>检测用户图形界面中载入参数的更改</td>
  </tr>
  <tr>
    <td>check_overwrite</td>
    <td>若目标路径有计算结果，选择是否覆盖（仅针对PAC设备）</td>
  </tr>
  <tr>
    <td>load_data</td>
    <td>根据设备、载入模式以及参数加载声发射数据</td>
  </tr>
  <tr>
    <td>波形分析模块</td>
    <td>功能简述</td>
  </tr>
  <tr>
    <td>check_chan</td>
    <td>根据用户选择切换不同的采集通道</td>
  </tr>
  <tr>
    <td>random_select</td>
    <td>随机选择当前通道的一个声发射信号编号</td>
  </tr>
  <tr>
    <td>show_waveform</td>
    <td>根据信号编号以及时频图模式进行可视化</td>
  </tr>
  <tr>
    <td>特征分析模块</td>
    <td>功能简述</td>
  </tr>
  <tr>
    <td>show_feature</td>
    <td>根据用户选择进行对应的统计分析</td>
  </tr>
  <tr>
    <td>load_stretcher</td>
    <td>加载万能试验机的应力应变数据</td>
  </tr>
</table>  
模块内部关系结构如下图所示：  
<div align=center>
<img src="/MD_figs/系统模块内部关系图.png" height="400px">
</div>
其中check_parameter功能同时适配IO模块与特征分析模块，分别用于对数据的初始载入与筛选。check_chan功能也同时适配波形分析模块与特征分析模块，能够对不同采集通道的数据分别进行分析。
### 设计和描述
本软件致力于集成声发射数据计算分析的多种模块，主要功能是实现以声发射数据为基础，通过波形提取、傅里叶变换、同步压缩小波变换、统计方法分析声发射信号，软件重点是能够根据不同声发射设备进行读取模式与计算模式的切换，进而为用户提供实验数据指导，辅助用户进行声发射信号与变形机制对应关系的理解。   
<div align=center>
<img src="/MD_figs/软件架构图.png" height="400px">
</div>  
## 软件功能描述
### 软件激活
运行软件时会先读取最近一次修改的license文件，若根据用户主机mac地址计算得出的时间远于当前系统时间，软件激活成功，否则需要重新上传license以替换旧文件。  
功能流程图如下图所示：  
<div align=center>
<img src="/MD_figs/软件激活功能流程图.png" height="400px">
</div>  
初次运行软件时激活窗口如下所示:  
<div align=center>
<img src="/MD_figs/active_1.png" height="400px">
</div>  
激活成功窗口如下所示：  
<div align=center>
<img src="/MD_figs/active_2.png" height="400px">
</div>  
License过期窗口如下所示：  
<div align=center>
<img src="/MD_figs/active_3.png" height="400px">
</div>  
### License更新
成功激活软件进入Visualization界面后，可以选择更新License信息。其中，只有当根据新导入License文件计算出的激活期限长于当前License文件的激活期限时，才允许更新此凭证。  
功能流程图如下图所示：  
<div align=center>
<img src="/MD_figs/License更新功能流程图.png" height="400px">
</div>  
新导入的License期限短于当前License时的窗口如下所示：  
<div align=center>
<img src="/MD_figs/updateLicense_1.png" height="400px">
</div>  
新导入的License期限长于当前License时的窗口如下所示：  
<div align=center>
<img src="/MD_figs/updateLicense_2.png" height="400px">
</div>  
### 设备切换与数据导入
针对不同的声发射设备，分别嵌入了相应的数据计算与载入算法。对于Vallen设备，由于该设备采样率较高，数据精度较好，不需要通过波形重新计算特征，故只提供了不同的数据载入模式。用户可选择仅载入波形、仅载入特征或同时载入波形与特征这三种不同的模式进行数据的读取。对于PAC设备，由于其采样率较低，特征精度损失较大，需要对波形重新计算相关特征，因此除了以上三种载入模式外，还添加了计算模式，并可配合相应的数据路径判断是否需要覆盖原始特征文件。此外，由于PAC设备输出的为经前置放大的信号，故在计算时额外添加了阈值选项。  
功能流程图如下图所示：  
<div align=center>
<img src="/MD_figs/设备切换与数据导入功能流程图.png" height="400px">
</div>  
Vallen设备数据载入模式窗口如下所示：  
<div align=center>
<img src="/MD_figs/LoadData_1.png" height="400px">
</div>  
PAC设备数据载入模式（无覆盖）窗口如下所示：  
<div align=center>
<img src="/MD_figs/LoadData_2.png" height="400px">
</div>  
PAC设备数据载入模式（覆盖）窗口如下所示：  
<div align=center>
<img src="/MD_figs/LoadData_3.png" height="400px">
</div>  
### 波形分析
若选取了读取波形的数据载入模式，则可进行如下波形分析。首先需要选择相应采集通道的信号，手动输入或者随机产生该通道内信号的序号，如有需要也可输入图注。若要进行时频域分析，可勾选频率选项，这里默认采取了同步压缩小波变化，因为该方法能够更好地呈现信号的时频关联特征。  
功能流程图如下图所示：  
<div align=center>
<img src="/MD_figs/波形分析功能流程图.png" height="400px">
</div>  
可视化成功窗口如下所示：  
<div align=center>
<img src="/MD_figs/waveform_1.png" height="400px">
</div>  
可视化时提示报错窗口如下所示：  
<div align=center>
<img src="/MD_figs/waveform_2.png" height="400px">
</div>  
### 数据筛选
若选取了读取特征的数据载入模式，则可进行如下数据筛选。首先需要选择相应采集通道的信号，然后可以从时间、振铃数、能量、振幅以及持续时间五个特征上对数据进行筛选，默认时间从初始开始，振铃数大于贰，能量、振幅和持续时间均大于零。若筛选后的数据个数为零，则会提示一个警告信息，用户需检查采集通道以及特征阈值的选择是否不合适。  
功能流程图如下图所示：  
<div align=center>
<img src="/MD_figs/数据筛选功能流程图.png" height="400px">
</div>  
筛选成功窗口如下所示：  
<div align=center>
<img src="/MD_figs/filter_1.png" height="400px">
</div>  
重置筛选窗口如下所示：  
<div align=center>
<img src="/MD_figs/filter_2.png" height="400px">
</div>  
筛选提示警告窗口如下所示：  
<div align=center>
<img src="/MD_figs/filter_3.png" height="400px">
</div>  
### 特征分析
若选取了读取特征的数据载入模式，则可进行如下特征分析。首先需要选择相应采集通道的信号，然后进行数据筛选，若筛选成功，会根据设备的不同激活相应功能选项。针对PAC设备添加了对其设备计算特征的可视化分析，并支持导出数据。此外，还支持能量、振幅、持续时间的最大似然统计、概率密度分布统计、互补累积分布统计的计算，以及等待时间分布、巴斯定律和大森定律的计算。对于不同的统计定律，分别添加了拟合功能，并支持修改拟合数据的范围。也支持对特征间关联性的等高线可视化分析功能。  
功能流程图如下图所示：  
<div align=center>
<img src="/MD_figs/特征分析功能流程图.png" height="400px">
</div>  
概率密度分布统计分析（不拟合数据）窗口如下所示：  
<div align=center>
<img src="/MD_figs/statistics_1.png" height="400px">
</div>  
概率密度分布统计分析（拟合数据）窗口如下所示：  
<div align=center>
<img src="/MD_figs/statistics_2.png" height="400px">
</div>  
### 万能试验机数据载入
在进行特征分析时，支持导入万能试验机的应力应变数据，便于结合声发射结果进行分析。此外，支持对应力曲线进行平滑。  
功能流程图如下图所示：  
<div align=center>
<img src="/MD_figs/万能试验机数据载入功能流程图.png" height="400px">
</div>  
特征时域分析（未导入应力应变数据）窗口如下所示：  
<div align=center>
<img src="/MD_figs/stretcher_1.png" height="400px">
</div>  
特征时域分析（导入应力应变数据）窗口如下所示：  
<div align=center>
<img src="/MD_figs/stretcher_2.png" height="400px">
</div>  
特征时域分析（导入应力应变数据，平滑处理）窗口如下所示：  
<div align=center>
<img src="/MD_figs/stretcher_3.png" height="400px">
</div>  
## 操作流程
本软件的操作流程如图所示：  
<div align=center>
<img src="/MD_figs/操作流程图.png" height="400px">
</div>  
## 安装与维护
### 安装
初次运行该软件需先安装Microsoft Visual C++运行库。声发射数据文件支持Vallen设备导出的sqlite型数据库文件以及PAC设备导出的波形文本文件。
### 维护
运行结果可视化图形支持调整数据点颜色、标签等信息。如需后续处理，亦可将导出的文本文件导入其他软件进行后续分析。  
运行过程中，警告与错误会在软件下方状态栏给出提示，用户只需根据提示进行修改即可。此外，部分错误信息会在日志窗口单独显示，用户若在操作过程中发现软件无反应，可点击波形分析查看日志窗口的错误信息，以进行后续修改。
