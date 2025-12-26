import numpy as np
import matplotlib.pyplot as plt
import sys

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号

class VehicleAxleLoadCalculator:
    def __init__(self):
        # 车辆参数
        self.total_weight = 24700  # kg
        self.L1 = 1800  # mm，一二轴间距
        self.L2 = 4800  # mm，二三轴间距
        self.L3 = 1400  # mm，三四轴间距

        # 轴编号和位置
        self.axle_positions = {
            'axle1': 0,
            'axle2': self.L1,
            'axle3': self.L1 + self.L2,
            'axle4': self.L1 + self.L2 + self.L3
        }

        print("车辆参数初始化：")
        print(f"总重: {self.total_weight} kg")
        print(f"轴距: 1-2轴: {self.L1}mm, 2-3轴: {self.L2}mm, 3-4轴: {self.L3}mm")
        print(f"总轴距: {self.L1 + self.L2 + self.L3}mm")
        print(f"轴位置（从第一轴起）: {self.axle_positions}")
        print("-" * 50)

    def calculate_axle_loads_new_model(self, cg_position):
        """
        新模型：基于悬挂刚度相同和车架刚性的变形协调条件
        计算给定重心位置下的轴载荷
        cg_position: 重心距离第二轴的距离（mm），正值表示在第二轴之后，负值表示在第二轴之前
        """
        # 重心绝对位置（从第一轴起）
        cg_absolute = self.axle_positions['axle2'] + cg_position

        # 各轴的绝对位置（从第一轴起）
        x1 = self.axle_positions['axle1']  # 0
        x2 = self.axle_positions['axle2']  # L1
        x3 = self.axle_positions['axle3']  # L1 + L2
        x4 = self.axle_positions['axle4']  # L1 + L2 + L3

        # 计算各轴相对于重心的水平坐标
        # 规定：重心前方为正，重心后方为负
        d1 = x1 - cg_absolute  # 第一轴到重心的距离
        d2 = x2 - cg_absolute  # 第二轴到重心的距离
        d3 = x3 - cg_absolute  # 第三轴到重心的距离
        d4 = x4 - cg_absolute  # 第四轴到重心的距离

        # 计算 S1 = Σd_i 和 S2 = Σd_i²
        d_list = [d1, d2, d3, d4]
        S1 = sum(d_list)
        S2 = sum(d_i ** 2 for d_i in d_list)

        W = self.total_weight

        # 计算分母，检查是否为零
        denominator = 4 * S2 - S1 ** 2

        if abs(denominator) < 1e-10:
            print(f"警告: 重心位置{cg_position}mm导致分母接近零，使用旧模型计算")
            return self.calculate_axle_loads_old(cg_position)

        # 计算每个轴的载荷：F_i = W * (S2 - S1 * d_i) / (4*S2 - S1^2)
        F1 = W * (S2 - S1 * d1) / denominator
        F2 = W * (S2 - S1 * d2) / denominator
        F3 = W * (S2 - S1 * d3) / denominator
        F4 = W * (S2 - S1 * d4) / denominator

        # 计算总轴载荷
        front_axle_load = F1 + F2  # 第一、二轴总载荷
        rear_axle_load = F3 + F4  # 第三、四轴总载荷

        return {
            'cg_position': cg_position,
            'cg_absolute': cg_absolute,
            'axle1_load': F1,
            'axle2_load': F2,
            'axle3_load': F3,
            'axle4_load': F4,
            'front_total': front_axle_load,
            'rear_total': rear_axle_load,
            'front_per_axle_avg': front_axle_load / 2,
            'rear_per_axle_avg': rear_axle_load / 2
        }

    def calculate_axle_loads_old(self, cg_position):
        """
        旧模型：对重心取矩，但假设一二轴载荷相等，三四轴载荷相等
        """
        # 重心绝对位置（从第一轴起）
        cg_absolute = self.axle_positions['axle2'] + cg_position

        W = self.total_weight
        L1 = self.L1
        L2 = self.L2
        L3 = self.L3
        d = cg_position  # 重心距离第二轴的距离

        denominator = 2 * (L1 + 2 * L2 + L3)

        # 计算第三、四轴载荷（每轴）
        y = (W * (L1 + 2 * d)) / denominator

        # 计算第一、二轴载荷（每轴）
        x = (W - 2 * y) / 2

        # 计算总轴载荷
        front_axle_load = 2 * x
        rear_axle_load = 2 * y

        return {
            'cg_position': cg_position,
            'cg_absolute': cg_absolute,
            'axle1_load': x,
            'axle2_load': x,
            'axle3_load': y,
            'axle4_load': y,
            'front_total': front_axle_load,
            'rear_total': rear_axle_load,
            'front_per_axle_avg': x,
            'rear_per_axle_avg': y
        }

    def compare_models(self, cg_range=(0, 4800), step=400):
        """
        比较新旧模型的差异
        """
        print("=" * 60)
        print("新旧模型比较分析")
        print("=" * 60)

        positions = np.arange(cg_range[0], cg_range[1] + step, step)

        for pos in positions:
            new_result = self.calculate_axle_loads_new_model(pos)
            old_result = self.calculate_axle_loads_old(pos)

            print(f"\n重心位置（距第二轴）: {pos:6}mm")
            print(f"  {'轴':<5} {'新模型(kg)':<12} {'旧模型(kg)':<12} {'差异(kg)':<10} {'差异(%)':<8}")
            print(f"  {'-' * 50}")

            for axle in [1, 2, 3, 4]:
                new_load = new_result[f'axle{axle}_load']
                old_load = old_result[f'axle{axle}_load']
                diff = new_load - old_load
                diff_percent = diff / old_load * 100 if old_load != 0 else 0

                print(f"  第{axle}轴 {new_load:10.1f} {old_load:10.1f} {diff:10.1f} {diff_percent:7.1f}%")

            new_front_total = new_result['front_total']
            old_front_total = old_result['front_total']
            new_rear_total = new_result['rear_total']
            old_rear_total = old_result['rear_total']

            print(
                f"\n  前轴总和: {new_front_total:10.1f} {old_front_total:10.1f} {new_front_total - old_front_total:10.1f} {(new_front_total - old_front_total) / old_front_total * 100:7.1f}%")
            print(
                f"  后轴总和: {new_rear_total:10.1f} {old_rear_total:10.1f} {new_rear_total - old_rear_total:10.1f} {(new_rear_total - old_rear_total) / old_rear_total * 100:7.1f}%")

    def analyze_load_distribution(self, cg_range=(0, 4800), step=100):
        """分析重心在指定范围内移动时的轴载荷分布"""
        print("开始分析轴载荷分布...")

        # 生成重心位置数组
        cg_positions = np.arange(cg_range[0], cg_range[1] + step, step)

        results = []
        for cg_pos in cg_positions:
            new_result = self.calculate_axle_loads_new_model(cg_pos)
            results.append(new_result)

            # 打印一些关键位置的结果
            if cg_pos in [0, 600, 1200, 1800, 2400, 3000, 3600, 4200, 4800]:
                print(f"重心位置（距第二轴）: {cg_pos:6}mm, "
                      f"前轴载荷: {new_result['front_total']:7.1f}kg, "
                      f"后轴载荷: {new_result['rear_total']:7.1f}kg")

        return results

    def plot_load_distribution(self, results):
        """绘制轴载荷分布图"""
        # 提取数据
        cg_positions = [r['cg_position'] for r in results]
        front_loads = [r['front_total'] for r in results]
        rear_loads = [r['rear_total'] for r in results]
        axle1_loads = [r['axle1_load'] for r in results]
        axle3_loads = [r['axle3_load'] for r in results]

        # 创建图形
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 图1：前后轴总载荷随重心位置变化
        ax1 = axes[0, 0]
        ax1.plot(cg_positions, front_loads, 'b-', linewidth=2, label='前轴总载荷 (1+2轴)')
        ax1.plot(cg_positions, rear_loads, 'r-', linewidth=2, label='后轴总载荷 (3+4轴)')
        ax1.axhline(y=self.total_weight / 2, color='gray', linestyle='--', alpha=0.5, label='总重一半')
        ax1.set_xlabel('重心位置（距离第二轴, mm）')
        ax1.set_ylabel('轴载荷 (kg)')
        ax1.set_title('前后轴总载荷随重心位置变化')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_xlim(min(cg_positions), max(cg_positions))

        # 图2：单轴载荷随重心位置变化
        ax2 = axes[0, 1]
        ax2.plot(cg_positions, axle1_loads, 'b-', linewidth=2, label='第一轴载荷')
        ax2.plot(cg_positions, axle3_loads, 'r-', linewidth=2, label='第三轴载荷')
        ax2.axhline(y=self.total_weight / 4, color='gray', linestyle='--', alpha=0.5, label='平均载荷')
        ax2.set_xlabel('重心位置（距离第二轴, mm）')
        ax2.set_ylabel('单轴载荷 (kg)')
        ax2.set_title('单轴载荷随重心位置变化')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.set_xlim(min(cg_positions), max(cg_positions))

        # 图3：载荷分配比例
        ax3 = axes[1, 0]
        front_percentage = [f / self.total_weight * 100 for f in front_loads]
        rear_percentage = [r / self.total_weight * 100 for r in rear_loads]
        ax3.plot(cg_positions, front_percentage, 'b-', linewidth=2, label='前轴载荷比例')
        ax3.plot(cg_positions, rear_percentage, 'r-', linewidth=2, label='后轴载荷比例')
        ax3.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='50%')
        ax3.set_xlabel('重心位置（距离第二轴, mm）')
        ax3.set_ylabel('载荷比例 (%)')
        ax3.set_title('载荷分配比例随重心位置变化')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        ax3.set_xlim(min(cg_positions), max(cg_positions))
        ax3.set_ylim(0, 100)

        # 图4：车辆示意图和当前载荷分布
        ax4 = axes[1, 1]
        ax4.axis('off')

        # 获取中间位置的结果（重心在第二轴处）
        middle_idx = len(results) // 2
        mid_result = results[middle_idx]

        # 绘制车辆示意图
        ax4.text(0.5, 0.9, '车辆轴距示意图', ha='center', va='center', fontsize=12, fontweight='bold')

        # 绘制轴位置
        ax_positions = list(self.axle_positions.values())
        ax_names = list(self.axle_positions.keys())

        for i, (pos, name) in enumerate(zip(ax_positions, ax_names)):
            ax4.plot([pos / 10000, pos / 10000], [0.7, 0.8], 'k-', linewidth=2)  # 轴
            ax4.scatter(pos / 10000, 0.75, s=100, c='black', zorder=5)
            ax4.text(pos / 10000, 0.65, f'{name}\n{pos}mm', ha='center', va='top', fontsize=9)

        # 绘制轴距线
        for i in range(len(ax_positions) - 1):
            ax4.plot([ax_positions[i] / 10000, ax_positions[i + 1] / 10000], [0.75, 0.75], 'k-', linewidth=1, alpha=0.5)
            dist = ax_positions[i + 1] - ax_positions[i]
            mid_x = (ax_positions[i] + ax_positions[i + 1]) / 2 / 10000
            ax4.text(mid_x, 0.77, f'{dist}mm', ha='center', va='bottom', fontsize=8, alpha=0.7)

        # 显示当前载荷
        ax4.text(0.5, 0.4, '当前载荷分布示例（重心在第二轴处）:', ha='center', va='center', fontsize=10)
        ax4.text(0.5, 0.35, f"总重: {self.total_weight} kg", ha='center', va='center', fontsize=9)
        ax4.text(0.5, 0.30, f"第一轴: {mid_result['axle1_load']:.1f} kg", ha='center', va='center', fontsize=9,
                 color='blue')
        ax4.text(0.5, 0.27, f"第二轴: {mid_result['axle2_load']:.1f} kg", ha='center', va='center', fontsize=9,
                 color='blue')
        ax4.text(0.5, 0.24, f"第三轴: {mid_result['axle3_load']:.1f} kg", ha='center', va='center', fontsize=9,
                 color='red')
        ax4.text(0.5, 0.21, f"第四轴: {mid_result['axle4_load']:.1f} kg", ha='center', va='center', fontsize=9,
                 color='red')
        ax4.text(0.5, 0.17,
                 f"前轴总载荷: {mid_result['front_total']:.1f} kg ({mid_result['front_total'] / self.total_weight * 100:.1f}%)",
                 ha='center', va='center', fontsize=9, color='blue')
        ax4.text(0.5, 0.14,
                 f"后轴总载荷: {mid_result['rear_total']:.1f} kg ({mid_result['rear_total'] / self.total_weight * 100:.1f}%)",
                 ha='center', va='center', fontsize=9, color='red')

        plt.suptitle(f'8×8车辆轴载荷分布分析 新模型 (总重: {self.total_weight}kg)', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

        return fig

    def find_special_points(self, results):
        """找出特殊点：载荷均衡点、最大最小载荷点等"""
        print("\n特殊点分析：")

        # 寻找前后轴载荷相等点
        min_diff = float('inf')
        equilibrium_point = None

        for r in results:
            diff = abs(r['front_total'] - r['rear_total'])
            if diff < min_diff:
                min_diff = diff
                equilibrium_point = r

        if equilibrium_point:
            print(f"1. 载荷均衡点（前后轴载荷最接近）:")
            print(f"   重心位置: {equilibrium_point['cg_position']:.0f}mm (距第二轴)")
            print(
                f"   前轴载荷: {equilibrium_point['front_total']:.1f}kg ({equilibrium_point['front_total'] / self.total_weight * 100:.1f}%)")
            print(
                f"   后轴载荷: {equilibrium_point['rear_total']:.1f}kg ({equilibrium_point['rear_total'] / self.total_weight * 100:.1f}%)")

        # 寻找最大前轴载荷点
        max_front = max(results, key=lambda x: x['front_total'])
        print(f"\n2. 最大前轴载荷点:")
        print(f"   重心位置: {max_front['cg_position']:.0f}mm (距第二轴)")
        print(
            f"   前轴载荷: {max_front['front_total']:.1f}kg ({max_front['front_total'] / self.total_weight * 100:.1f}%)")

        # 寻找最大后轴载荷点
        max_rear = max(results, key=lambda x: x['rear_total'])
        print(f"\n3. 最大后轴载荷点:")
        print(f"   重心位置: {max_rear['cg_position']:.0f}mm (距第二轴)")
        print(f"   后轴载荷: {max_rear['rear_total']:.1f}kg ({max_rear['rear_total'] / self.total_weight * 100:.1f}%)")

def main():
    # 创建车辆轴载荷计算器
    calculator = VehicleAxleLoadCalculator()

    cg_range = (0, 4800)
    step = 50  # 步长

    # 分析轴载荷分布
    results = calculator.analyze_load_distribution(cg_range, step)

    # 绘制图表
    fig = calculator.plot_load_distribution(results)

    # 找出特殊点
    calculator.find_special_points(results)

    # 对比新旧模型
    sys.stdout = open('output.txt', 'w', encoding="utf-8")
    calculator.compare_models(cg_range, step)
    sys.stdout = sys.__stdout__
'''
    # 计算几个特定重心位置的轴载荷
    print("\n特定重心位置的轴载荷计算：")
    test_positions = [0, 1200, 2400, 3600, 4800]

    for pos in test_positions:
        result = calculator.calculate_axle_loads_new_model(pos)
        print(f"\n重心位置（距第二轴）: {pos}mm")
        print(f"  第一轴载荷: {result['axle1_load']:.1f} kg")
        print(f"  第二轴载荷: {result['axle2_load']:.1f} kg")
        print(f"  第三轴载荷: {result['axle3_load']:.1f} kg")
        print(f"  第四轴载荷: {result['axle4_load']:.1f} kg")
        print(
            f"  前轴总载荷: {result['front_total']:.1f} kg ({result['front_total'] / calculator.total_weight * 100:.1f}%)")
        print(
            f"  后轴总载荷: {result['rear_total']:.1f} kg ({result['rear_total'] / calculator.total_weight * 100:.1f}%)")
'''

if __name__ == "__main__":
    main()