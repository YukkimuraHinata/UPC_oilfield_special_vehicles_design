# UPC_oilfield_special_vehicles_design
本仓库源于中国石油大学（华东）（UPC）车辆工程专业综合设计:<br>
油田用钢制连续抽油杆作业车设计，在对石油特车的动力性与轴载荷分配的计算过程中所使用的python代码

其实代码大部分是deepseek写的（<br>
下面是我们所选用的二类底盘的参数：<br>
![底盘参数](/pic/car_profile.png "国六新车，放心大胆的抄")<br>
calculate.py简单的将两前轴的载荷视为相等，两后轴的载荷相等，<br>
这样简单的将四轴车辆简化为二力杆。<br>

而calculate_new则是升级版本，它假设载荷与重心的距离成反比<br>
![化简出的公式](/pic/formula.png "轴载荷与距离的关系")<br>
![哎，就是懒](/pic/变量含义.png "太伟大了，D指导")<br>
同时，本模型假设：<br>
1.所有悬挂系统的刚度相同<br>
2.车架为绝对刚性<br>
3.悬挂变形量与载荷成正比(线性悬挂)<br>

dynamic_simulation则是车辆的动力性模拟<br>
（汽车理论这一块）<br>

就这样，感谢看到这里<br>
