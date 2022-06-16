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
## 软件功能描述
### 软件激活
运行软件时会先读取最近一次修改的license文件，若根据用户主机mac地址计算得出的时间远于当前系统时间，软件激活成功，否则需要重新上传license以替换旧文件。  
功能流程图如下图所示：  
<div align=center>
<img src="/MD_figs/软件激活功能流程图.png" width="250px">
</div>  
初次运行软件时激活窗口如下所示:  
<div align=center>
<img src="/MD_figs/active_1.png" width="250px">
</div>  
激活成功窗口如下所示：  
<div align=center>
<img src="/MD_figs/active_2.png" width="250px">
</div>  
License过期窗口如下所示：  
<div align=center>
<img src="/MD_figs/active_3.png" width="250px">
</div>  
### License更新

