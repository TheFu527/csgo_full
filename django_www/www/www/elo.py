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
        if rating >= 2300:
            return 8
        elif rating >= 2000:
            return 16
        else:
            return 24

    # 使用公式推算
    def computeScore(self, ratingA, ratingB):
        return 1 / (1 + pow(10, (ratingB - ratingA) / 400))

    # 计算新的ELO
    def getNewScore(self, old, k, SA, EA):
        return old + k * (SA - EA)
