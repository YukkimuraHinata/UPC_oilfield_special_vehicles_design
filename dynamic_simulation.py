import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号

class VehiclePerformanceAnalysis:
    """汽车性能分析类"""
    
    def __init__(self):
        # 车辆基本参数（示例值，可修改）
        self.m = 24700  # 整车质量 (kg)
        self.g = 9.81  # 重力加速度 (m/s²)
        self.rho = 1.204  # 空气密度 (kg/m³)
        self.Cd = 0.6  # 空气阻力系数
        self.A = 10.1  # 迎风面积 (m²)
        self.f = 0.05  # 滚动阻力系数
        self.eta_T = 0.9  # 传动系机械效率
        self.r = 0.8235  # 车轮半径 (m)
        
        # 变速器传动比（16档手动变速箱示例）
        self.gear_ratios = {
            '1档': 13.8,
            '2档': 11.54,
            '3档': 9.49,
            '4档': 7.93,
            '5档': 6.53,
            '6档': 5.46,
            '7档': 4.57,
            '8档': 3.82,
            '9档': 3.02,
            '10档': 2.53,
            '11档': 2.08,
            '12档': 1.74,
            '13档': 1.43,
            '14档': 1.2,
            '15档': 1.0,
            '16档': 0.84,
        }
        self.final_drive_ratio = 6.727  # 主减速器传动比
        
        # 发动机外特性数据（示例）
        self.engine_speed = np.array([800, 1000, 1200, 1400, 1600, 1800, 1900, 2000, 2100, 2200])  # 转速 (rpm)
        self.engine_torque = np.array([2000, 2300, 2300, 2300, 2086, 1885, 1789, 1684, 1580, 1475])  # 扭矩 (N·m)
    
    def calculate_tractive_force(self, gear_name):
        """计算驱动力"""
        ig = self.gear_ratios[gear_name]  # 变速器传动比
        i0 = self.final_drive_ratio  # 主减速器传动比
        
        # 车速计算 (km/h): v = 0.377 * n * r / (ig * i0)
        vehicle_speed = 0.377 * self.engine_speed * self.r / (ig * i0)
        
        # 驱动力计算 (N): Ft = Ttq * ig * i0 * eta_T / r
        tractive_force = self.engine_torque * ig * i0 * self.eta_T / self.r
        
        return vehicle_speed, tractive_force
    
    def calculate_resistance_force(self, vehicle_speed_kmh):
        """计算行驶阻力"""
        # 确保vehicle_speed_kmh是numpy数组
        vehicle_speed_kmh = np.asarray(vehicle_speed_kmh)
        
        # 转换为m/s
        vehicle_speed_ms = vehicle_speed_kmh / 3.6
        
        # 滚动阻力 (N): Ff = m * g * f
        rolling_resistance = self.m * self.g * self.f * np.ones_like(vehicle_speed_kmh)
        
        # 空气阻力 (N): Fw = 0.5 * Cd * A * rho * v²
        air_resistance = 0.5 * self.Cd * self.A * self.rho * vehicle_speed_ms**2
        
        # 坡度阻力（假设平路为0）
        grade_resistance = np.zeros_like(vehicle_speed_kmh)
        
        # 总行驶阻力
        total_resistance = rolling_resistance + air_resistance + grade_resistance
        
        return {
            'total': total_resistance,
            'rolling': rolling_resistance,
            'air': air_resistance,
            'grade': grade_resistance
        }
    
    def plot_tractive_resistance_balance(self):
        """绘制驱动力-行驶阻力平衡图"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 存储各档位数据用于标注
        gear_data = {}
        
        # 绘制各档位驱动力曲线
        colors = plt.cm.Set2(np.linspace(0, 1, len(self.gear_ratios)))
        for i, (gear_name, color) in enumerate(zip(self.gear_ratios.keys(), colors)):
            v, ft = self.calculate_tractive_force(gear_name)
            line, = ax.plot(v, ft, 
                          linewidth=2.5, 
                          color=color,
                          marker='o',
                          markersize=4,
                          label=f'{gear_name}驱动力')
            gear_data[gear_name] = (v, ft, line)
            
            # 标注最大驱动力点
            max_idx = np.argmax(ft)
            if gear_name in ['1档', '15档']:  # 只标注1档和15档
                ax.annotate(f'Max {gear_name}', 
                           xy=(v[max_idx], ft[max_idx]),
                           xytext=(10, 10),
                           textcoords='offset points',
                           fontsize=9,
                           arrowprops=dict(arrowstyle='->', color=color, alpha=0.6))
        
        # 计算并绘制行驶阻力曲线
        speed_range = np.linspace(0, 220, 200)
        resistances = self.calculate_resistance_force(speed_range)
        
        # 总行驶阻力
        ax.plot(speed_range, resistances['total'], 
               'k--', linewidth=3, alpha=0.8, label='总行驶阻力(Ff+Fw)')
        
        # 分解阻力（可选显示）
        ax.plot(speed_range, resistances['rolling'], 
               'b:', linewidth=1.5, alpha=0.6, label='滚动阻力Ff')
        ax.plot(speed_range, resistances['air'], 
               'r:', linewidth=1.5, alpha=0.6, label='空气阻力Fw')
        
        # 标记最高车速（15档驱动力与总阻力的交点）
        v_15th, ft_15th = gear_data['15档'][0], gear_data['15档'][1]
        
        # 插值计算5档驱动力在整个速度范围内的值
        # 由于发动机转速点有限，需要插值到连续速度范围
        ft_15th_interp = np.interp(speed_range, v_15th, ft_15th)
        
        # 找到交点（驱动力 >= 总阻力）
        intersection_idx = np.where(ft_15th_interp >= resistances['total'])[0]
        
        if len(intersection_idx) > 0:
            # 最后一个交点对应最高车速
            max_speed_idx = intersection_idx[-1]
            max_speed = speed_range[max_speed_idx]
            max_speed_force = ft_15th_interp[max_speed_idx]
            
            # 标记最高车速点
            ax.plot(max_speed, max_speed_force, 'ro', markersize=10, zorder=5)
            ax.annotate(f'最高车速: {max_speed:.1f} km/h',
                       xy=(max_speed, max_speed_force),
                       xytext=(20, -30),
                       textcoords='offset points',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
                       arrowprops=dict(arrowstyle="->", color='red'))
        
        # 计算并标记各档位最大车速点
        for gear_name, color in zip(self.gear_ratios.keys(), colors):
            if gear_name != '15档':  # 5档已经处理过了
                v, ft = gear_data[gear_name][0], gear_data[gear_name][1]
                ft_interp = np.interp(speed_range, v, ft)
                idx = np.where(ft_interp >= resistances['total'])[0]
                if len(idx) > 0:
                    max_v = speed_range[idx[-1]]
                    ax.axvline(x=max_v, color=color, linestyle=':', alpha=0.3)
        
        # 设置图表属性
        ax.set_xlabel('车速 (km/h)', fontsize=14, fontweight='bold')
        ax.set_ylabel('力 (N)', fontsize=14, fontweight='bold')
        ax.set_title('汽车驱动力-行驶阻力平衡图', fontsize=16, fontweight='bold', pad=20)
        
        # 设置坐标轴范围
        ax.set_xlim([0, 120])
        ax.set_ylim([0, 240000])
        
        # 添加网格
        ax.grid(True, which='both', linestyle='--', alpha=0.7)
        
        # 添加图例
        ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
        
        # 添加文字说明框
        textstr = '\n'.join((
            f'车辆参数:',
            f'质量: {self.m} kg',
            f'Cd: {self.Cd}',
            f'A: {self.A} m^2',
            f'f: {self.f}',
            f'η_T: {self.eta_T}'
        ))
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        return fig, ax
    
    def plot_power_balance(self):
        """绘制功率平衡图"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 计算行驶阻力功率
        speed_range = np.linspace(0, 120, 100)
        resistances = self.calculate_resistance_force(speed_range)
        resistance_power_kw = resistances['total'] * (speed_range / 3.6) / 1000
        
        # 绘制各档位功率曲线
        colors = plt.cm.Set2(np.linspace(0, 1, len(self.gear_ratios)))
        for gear_name, color in zip(self.gear_ratios.keys(), colors):
            v, ft = self.calculate_tractive_force(gear_name)
            # 插值到连续速度范围
            v_cont = np.linspace(min(v), max(v), 100)
            ft_interp = np.interp(v_cont, v, ft)
            # 功率 = 力 × 速度 (转换为kW)
            power_kw = ft_interp * (v_cont / 3.6) / 1000
            ax.plot(v_cont, power_kw, linewidth=2, color=color, label=f'{gear_name}功率')
        
        ax.plot(speed_range, resistance_power_kw, 'k--', linewidth=2.5, label='行驶阻力功率')
        
        ax.set_xlabel('车速 (km/h)', fontsize=12)
        ax.set_ylabel('功率 (kW)', fontsize=12)
        ax.set_title('汽车功率平衡图', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, 120])
        
        return fig, ax
    
    def plot_acceleration_performance(self):
        """绘制加速度曲线"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        speed_range = np.linspace(10, 120, 100)  # 从10km/h开始避免除零
        resistances = self.calculate_resistance_force(speed_range)
        
        colors = plt.cm.Set2(np.linspace(0, 1, len(self.gear_ratios)))
        
        for gear_name, color in zip(self.gear_ratios.keys(), colors):
            v_gear, ft_gear = self.calculate_tractive_force(gear_name)
            # 插值计算该档位在整个速度范围内的驱动力
            ft_interp = np.interp(speed_range, v_gear, ft_gear)
            
            # 计算加速度: a = (Ft - F_resistance) / (m * δ)
            # 其中δ是旋转质量换算系数，这里简化取1.05
            delta = 1.05  # 旋转质量换算系数
            acceleration = (ft_interp - resistances['total']) / (self.m * delta)
            
            # 转换为m/s²，并过滤负值
            acceleration = np.maximum(acceleration, 0)
            
            ax.plot(speed_range, acceleration, linewidth=2, color=color, label=f'{gear_name}')
        
        ax.set_xlabel('车速 (km/h)', fontsize=12)
        ax.set_ylabel('加速度 (m/s^2)', fontsize=12)
        ax.set_title('汽车加速度曲线', fontsize=14, fontweight='bold')
        ax.legend(title='档位')
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, 120])
        ax.set_ylim([0, 8])
        
        return fig, ax
    
    def calculate_performance_indicators(self):
        """计算性能指标"""
        # 计算行驶阻力
        speed_range = np.linspace(0, 220, 500)
        resistances = self.calculate_resistance_force(speed_range)
        
        # 最高车速（10档）
        v_15th, ft_15th = self.calculate_tractive_force('5档')
        ft_15th_interp = np.interp(speed_range, v_15th, ft_15th)
        intersection_idx = np.where(ft_15th_interp >= resistances['total'])[0]
        
        if len(intersection_idx) > 0:
            max_speed = speed_range[intersection_idx[-1]]
        else:
            max_speed = 0
        
        # 最大爬坡度（1档，在10km/h时计算）
        v_1st, ft_1st = self.calculate_tractive_force('1档')
        # 取10km/h附近的驱动力
        idx_10kmh = np.argmin(np.abs(v_1st - 10))
        max_tractive_force = ft_1st[idx_10kmh]
        
        # 在10km/h时的行驶阻力
        v_10kmh = 10
        resistances_at_10 = self.calculate_resistance_force(v_10kmh)
        
        # 爬坡度计算: sin(θ) = (Ft - Ff - Fw) / (m*g)
        available_force = max_tractive_force - resistances_at_10['total']
        if available_force > 0:
            sin_theta = available_force / (self.m * self.g)
            # 限制sin_theta在[0, 1]范围内
            sin_theta = min(max(sin_theta, 0), 0.5)  # 最大坡度限制在30°左右
            max_grade = np.arcsin(sin_theta) * 180 / np.pi  # 转换为角度
            max_grade_percent = np.tan(np.arcsin(sin_theta)) * 100  # 坡度百分比
        else:
            max_grade = 0
            max_grade_percent = 0
        
        # 计算0-100km/h加速时间（简化估算）
        # 使用平均加速度估算
        avg_acceleration = 2.5  # m/s² (典型值，实际应计算)
        accel_time = (100/3.6) / avg_acceleration  # 秒
        
        return {
            '最高车速 (km/h)': round(max_speed, 1),
            '最大爬坡度 (°)': round(max_grade, 1),
            '最大爬坡度 (%)': round(max_grade_percent, 1),
            '估算0-100km/h加速时间 (s)': round(accel_time, 1)
        }


def main():
    """主函数"""
    print("=" * 60)
    print("汽车驱动力-行驶阻力平衡分析系统")
    print("=" * 60)
    
    # 创建车辆分析对象
    vehicle = VehiclePerformanceAnalysis()
    
    # 计算性能指标
    print("\n正在计算性能指标...")
    performance = vehicle.calculate_performance_indicators()
    
    print("\n性能指标计算结果:")
    print("-" * 40)
    for key, value in performance.items():
        print(f"{key}: {value}")
    
    # 绘制图表
    print("\n正在生成图表...")
    
    # 1. 驱动力-行驶阻力平衡图
    fig1, ax1 = vehicle.plot_tractive_resistance_balance()
    
    # 2. 功率平衡图
    fig2, ax2 = vehicle.plot_power_balance()
    
    # 3. 加速度曲线图
    fig3, ax3 = vehicle.plot_acceleration_performance()
    
    # 保存图表
    fig1.savefig('驱动力-行驶阻力平衡图.png', dpi=300, bbox_inches='tight')
    fig2.savefig('功率平衡图.png', dpi=300, bbox_inches='tight')
    fig3.savefig('加速度曲线图.png', dpi=300, bbox_inches='tight')
    
    print("\n图表已保存:")
    print("1. 驱动力-行驶阻力平衡图.png")
    print("2. 功率平衡图.png")
    print("3. 加速度曲线图.png")
    
    # 显示图表
    plt.show()
'''    
    # 提供交互式参数修改功能
    print("\n" + "=" * 60)
    print("参数修改说明:")
    print("=" * 60)
    print("如需修改车辆参数，请在代码中修改VehiclePerformanceAnalysis类的参数:")
    print("1. 质量 m (kg)")
    print("2. 空气阻力系数 Cd")
    print("3. 迎风面积 A (m²)")
    print("4. 滚动阻力系数 f")
    print("5. 传动比 gear_ratios")
    print("6. 发动机外特性数据 engine_speed 和 engine_torque")

# 交互式参数设置函数（可选）
def interactive_analysis():
    """交互式参数设置和分析"""
    print("汽车性能分析交互模式")
    print("输入车辆参数（按Enter使用默认值）:")
    
    vehicle = VehiclePerformanceAnalysis()
    
    try:
        m = input(f"整车质量 (kg) [{vehicle.m}]: ")
        if m:
            vehicle.m = float(m)
            
        Cd = input(f"空气阻力系数 [{vehicle.Cd}]: ")
        if Cd:
            vehicle.Cd = float(Cd)
            
        A = input(f"迎风面积 (m²) [{vehicle.A}]: ")
        if A:
            vehicle.A = float(A)
            
        f = input(f"滚动阻力系数 [{vehicle.f}]: ")
        if f:
            vehicle.f = float(f)
            
        print("\n参数设置完成，开始分析...")
        
        # 重新计算和绘图
        performance = vehicle.calculate_performance_indicators()
        
        print("\n性能指标计算结果:")
        print("-" * 40)
        for key, value in performance.items():
            print(f"{key}: {value}")
        
        # 绘图
        fig1, _ = vehicle.plot_tractive_resistance_balance()
        fig2, _ = vehicle.plot_power_balance()
        
        plt.show()
        
    except ValueError as e:
        print(f"输入错误: {e}")
        print("请确保输入的是有效的数字")
'''

if __name__ == "__main__":
    # 直接运行主函数
    main()
    
    # 如果想使用交互模式，取消下面一行的注释
    # interactive_analysis()