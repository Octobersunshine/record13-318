from radar_chart_service import RadarChartService
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def example_basic():
    print("示例1: 基础雷达图 - 学生成绩对比")
    dimensions = ['语文', '数学', '英语', '物理', '化学', '生物']
    service = RadarChartService(dimensions=dimensions)

    service.add_entity("学生A", [85, 92, 78, 88, 90, 82])
    service.add_entity("学生B", [76, 88, 95, 70, 82, 78])
    service.add_entity("学生C", [90, 75, 80, 92, 78, 88])

    service.save("output/student_comparison.png",
                 title="学生成绩雷达图对比",
                 rmax=100, rsteps=5)
    print("已保存: output/student_comparison.png")


def example_with_dict_scores():
    print("\n示例2: 使用字典格式的分数 - 产品功能评估")
    dimensions = ['性能', '易用性', '稳定性', '扩展性', '安全性', '性价比', '售后服务']
    service = RadarChartService(dimensions=dimensions, frame='polygon')

    service.add_entity("产品X", {
        '性能': 8.5,
        '易用性': 9.0,
        '稳定性': 7.5,
        '扩展性': 6.0,
        '安全性': 8.0,
        '性价比': 9.2,
        '售后服务': 7.0
    }, color='#ff6b6b', alpha=0.3)

    service.add_entity("产品Y", {
        '性能': 9.2,
        '易用性': 7.5,
        '稳定性': 9.0,
        '扩展性': 8.5,
        '安全性': 9.5,
        '性价比': 6.5,
        '售后服务': 8.8
    }, color='#4ecdc4', alpha=0.3)

    service.save("output/product_comparison.png",
                 title="产品功能雷达图评估",
                 rmax=10, rsteps=5,
                 figsize=(9, 9))
    print("已保存: output/product_comparison.png")


def example_multiple_entities():
    print("\n示例3: 多实体对比 - 员工能力评估")
    dimensions = ['沟通能力', '技术能力', '团队协作', '创新能力', '执行力', '领导力']
    service = RadarChartService(dimensions=dimensions)

    employees = [
        {"name": "张三", "scores": [8, 9, 7, 6, 9, 5]},
        {"name": "李四", "scores": [9, 7, 9, 5, 8, 7]},
        {"name": "王五", "scores": [7, 8, 8, 9, 7, 6]},
        {"name": "赵六", "scores": [6, 9, 6, 8, 9, 8]},
        {"name": "钱七", "scores": [8, 6, 9, 7, 6, 9]},
    ]
    service.add_entities(employees)

    service.save("output/employee_comparison.png",
                 title="员工能力雷达图评估",
                 rmax=10, rsteps=5,
                 legend_loc='lower right',
                 bbox_to_anchor=(1.3, 0))
    print("已保存: output/employee_comparison.png")


def example_circle_frame():
    print("\n示例4: 圆形雷达图 - 运动员综合素质")
    dimensions = ['速度', '力量', '耐力', '柔韧性', '敏捷性', '协调性']
    service = RadarChartService(dimensions=dimensions, frame='circle')

    service.add_entity("运动员甲", [9.5, 8.0, 7.5, 6.5, 9.0, 8.5],
                       color='#e74c3c', alpha=0.2)
    service.add_entity("运动员乙", [7.0, 9.5, 9.0, 7.5, 7.0, 8.0],
                       color='#3498db', alpha=0.2)

    service.save("output/athlete_comparison.png",
                 title="运动员综合素质雷达图",
                 rmax=10, rsteps=5,
                 figsize=(8, 8))
    print("已保存: output/athlete_comparison.png")


def example_serialization():
    print("\n示例5: 序列化与反序列化")
    dimensions = ['维度1', '维度2', '维度3', '维度4', '维度5']
    service = RadarChartService(dimensions=dimensions)
    service.add_entity("实体A", [80, 90, 70, 85, 75])
    service.add_entity("实体B", [70, 80, 90, 65, 85])

    data = service.to_dict()
    print("序列化数据:", data)

    service2 = RadarChartService.from_dict(data)
    service2.save("output/serialization_example.png",
                  title="序列化/反序列化示例",
                  rmax=100)
    print("已保存: output/serialization_example.png")


if __name__ == "__main__":
    import os
    os.makedirs("output", exist_ok=True)

    example_basic()
    example_with_dict_scores()
    example_multiple_entities()
    example_circle_frame()
    example_serialization()

    print("\n所有示例运行完成！请查看 output 目录下的图片文件。")
