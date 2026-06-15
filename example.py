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


def example_normalize_different_scales():
    print("\n示例6: 不同量纲维度的归一化对比")

    dimensions = ['收入(万元)', '用户数(万)', '评分', '市场份额(%)', '增长率(%)']
    service_norm = RadarChartService(dimensions=dimensions, normalize=True)
    service_norm.add_entity("公司A", [5000, 800, 4.5, 35, 120])
    service_norm.add_entity("公司B", [3000, 1200, 4.8, 20, 80])
    service_norm.add_entity("公司C", [8000, 500, 3.9, 45, 50])

    service_norm.save("output/normalize_enabled.png",
                      title="归一化雷达图（不同量纲维度）",
                      rsteps=5)
    print("已保存: output/normalize_enabled.png")

    service_raw = RadarChartService(dimensions=dimensions, normalize=False)
    service_raw.add_entity("公司A", [5000, 800, 4.5, 35, 120])
    service_raw.add_entity("公司B", [3000, 1200, 4.8, 20, 80])
    service_raw.add_entity("公司C", [8000, 500, 3.9, 45, 50])

    service_raw.save("output/normalize_disabled.png",
                     title="未归一化雷达图（不同量纲维度 - 失真）",
                     rsteps=5)
    print("已保存: output/normalize_disabled.png")


def example_normalize_vs_raw():
    print("\n示例7: 同一数据归一化 vs 未归一化对比")

    dimensions = ['代码质量', '沟通效率', 'Bug率(个)', '代码行数(千)', '修复时长(小时)']
    service = RadarChartService(dimensions=dimensions, normalize=True)

    service.add_entity("开发者甲", [9.0, 7.5, 2, 50, 4])
    service.add_entity("开发者乙", [6.5, 9.0, 15, 20, 12])

    service.save("output/dev_comparison_normalized.png",
                 title="开发者能力雷达图（归一化）",
                 rsteps=5)
    print("已保存: output/dev_comparison_normalized.png")

    service_raw = RadarChartService(dimensions=dimensions, normalize=False)
    service_raw.add_entity("开发者甲", [9.0, 7.5, 2, 50, 4])
    service_raw.add_entity("开发者乙", [6.5, 9.0, 15, 20, 12])

    service_raw.save("output/dev_comparison_raw.png",
                     title="开发者能力雷达图（未归一化 - 失真）",
                     rsteps=5)
    print("已保存: output/dev_comparison_raw.png")


def example_group_stack():
    print("\n示例8: 分组叠加在同一张雷达图上（多组对比）")

    dimensions = ['攻击', '防御', '速度', '生命', '暴击', '法力']
    service = RadarChartService(dimensions=dimensions, normalize=True)

    warriors = [
        {"name": "战士·张飞", "scores": [88, 95, 60, 92, 55, 40]},
        {"name": "战士·关羽", "scores": [92, 88, 72, 85, 68, 45]},
        {"name": "战士·赵云", "scores": [85, 80, 82, 78, 75, 55]},
    ]
    mages = [
        {"name": "法师·诸葛亮", "scores": [90, 40, 65, 55, 85, 98]},
        {"name": "法师·司马懿", "scores": [88, 45, 70, 52, 90, 92]},
    ]
    archers = [
        {"name": "射手·黄忠", "scores": [95, 50, 68, 65, 92, 60]},
        {"name": "射手·孙尚香", "scores": [90, 42, 80, 58, 88, 65]},
    ]

    service.add_group("战士阵营", warriors)
    service.add_group("法师阵营", mages)
    service.add_group("射手阵营", archers)

    service.save("output/group_stacked.png",
                 title="多阵营英雄能力对比（分组叠加）",
                 rsteps=5,
                 figsize=(10, 9),
                 bbox_to_anchor=(1.35, 0))
    print("已保存: output/group_stacked.png")


def example_multi_subplot_by_group():
    print("\n示例9: 多子图并排对比（按组拆分）")

    dimensions = ['语文', '数学', '英语', '物理', '化学', '生物', '历史']
    service = RadarChartService(dimensions=dimensions, normalize=True)

    class_a = [
        {"name": "小明", "scores": [85, 90, 78, 88, 82, 80, 75]},
        {"name": "小红", "scores": [92, 78, 95, 72, 78, 82, 88]},
    ]
    class_b = [
        {"name": "小李", "scores": [78, 88, 82, 90, 85, 78, 80]},
        {"name": "小张", "scores": [80, 92, 75, 85, 88, 90, 72]},
    ]
    class_c = [
        {"name": "小王", "scores": [88, 85, 80, 82, 90, 85, 78]},
        {"name": "小刘", "scores": [75, 95, 72, 92, 82, 78, 85]},
    ]

    service.add_group("一班", class_a)
    service.add_group("二班", class_b)
    service.add_group("三班", class_c)

    layouts = [
        {"groups": ["一班"], "title": "一班学生成绩"},
        {"groups": ["二班"], "title": "二班学生成绩"},
        {"groups": ["三班"], "title": "三班学生成绩"},
        {"groups": ["一班", "二班", "三班"], "title": "全员对比"},
    ]
    service.save_multi("output/multi_subplot_groups.png",
                       layouts=layouts,
                       ncols=2,
                       figsize=(14, 12),
                       share_legend=True,
                       super_title="各班级学生成绩雷达图对比")
    print("已保存: output/multi_subplot_groups.png")


def example_multi_subplot_custom():
    print("\n示例10: 多子图对比（自定义筛选条件）")

    dimensions = ['收入(万元)', '用户数(万)', '评分', '市场份额(%)', '增长率(%)', '利润率(%)']
    service = RadarChartService(dimensions=dimensions, normalize=True)

    companies = [
        {"name": "Alpha", "scores": [8000, 1200, 4.6, 30, 90, 25], "group": "大型"},
        {"name": "Beta",  "scores": [5000, 800,  4.3, 22, 75, 20], "group": "中型"},
        {"name": "Gamma", "scores": [15000, 2000, 4.8, 45, 60, 30], "group": "大型"},
        {"name": "Delta", "scores": [2000, 400, 4.0, 10, 120, 15], "group": "中型"},
        {"name": "Eps",   "scores": [800,  200, 4.2, 5,  150, 12], "group": "小型"},
        {"name": "Zeta",  "scores": [500,  150, 4.5, 3,  180, 18], "group": "小型"},
    ]
    service.add_entities(companies)

    layouts = [
        {
            "title": "大型企业",
            "filter": lambda e: e.get('group') == '大型'
        },
        {
            "title": "中型企业",
            "filter": lambda e: e.get('group') == '中型'
        },
        {
            "title": "小型企业",
            "filter": lambda e: e.get('group') == '小型'
        },
        {
            "title": "高增长企业（>100%）",
            "filter": lambda e: e['scores'][4] > 100
        },
    ]
    service.save_multi("output/multi_subplot_custom.png",
                       layouts=layouts,
                       ncols=2,
                       figsize=(14, 12),
                       share_legend=True,
                       super_title="企业多维度指标分场景对比")
    print("已保存: output/multi_subplot_custom.png")


if __name__ == "__main__":
    import os
    os.makedirs("output", exist_ok=True)

    example_basic()
    example_with_dict_scores()
    example_multiple_entities()
    example_circle_frame()
    example_serialization()
    example_normalize_different_scales()
    example_normalize_vs_raw()
    example_group_stack()
    example_multi_subplot_by_group()
    example_multi_subplot_custom()

    print("\n所有示例运行完成！请查看 output 目录下的图片文件。")
