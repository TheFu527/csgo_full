class EloScore:

    # 定义胜负关系
    ELO_RESULT_WIN = 1
    ELO_RESULT_LOSS = -1
    ELO_RESULT_TIE = 0

    # 初始积分
    ELO_RATING_DEFAULT = 1500

    # 排名
    ratingA = 0
    ratingB = 0

    # 定义初始化方法
    def __init__(self, ratingA=ELO_RATING_DEFAULT, ratingB=ELO_RATING_DEFAULT):
        self.ratingA = ratingA
        self.ratingB = ratingB

    # 定义阈值 k值
    def computeK(self, rating):
        if rating >= 2400:
            return 8
        elif rating >= 2100:
            return 16
        else:
            return 24

    # 使用公式推算
    def computeScore(self, rating1, rating2):
        return 1 / (1+pow(10, (rating2-rating1)/400))


if __name__ == "__main__":
    # 实例化一个对象
    eloscore = EloScore()
    # 打印胜率
    print(eloscore.computeScore(1500, 1800))
    # 打印等级
    print(eloscore.computeK(1500))
    print(eloscore.computeK(1800))
