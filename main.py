import pandas as pd

cells = []  # 確定させたセル
temp_cells = []  # 確定前のセル
sorted_temp_cells = []  # 重み順にならべた確定前のセル
labors = []  # 労働者リスト

DAY_PER_WEEK = 3  # 一周あたりの日数
CELL_PER_DAY = 2  # 一日あたりのセルの数


def search_cell_groupe_ids(id):
    id = int(id)
    cell_ids = []
    mod = id % CELL_PER_DAY
    id = id - mod + 1
    for i in range(id, id + CELL_PER_DAY, 1):
        cell_ids.append(i)
    return cell_ids


class cell(object):
    labor_ids = []

    def __init__(self, cell_id, labor_id, need):
        self.cell_id = cell_id
        self.labor_id = labor_id
        self.need = need
        cells.append(self)


class temp_cell(object):
    weight = 0

    def __init__(self, cell_id, need, can_work_labor_id):
        self.cell_id = cell_id
        self.need = need
        self.can_work_labor_ids = can_work_labor_id
        temp_cells.append(self)

    def calc_weight(self):
        self.weight = int((len(self.can_work_labor_ids) + 1) / 2) - self.need

    def confirm_need(self):
        if self.need > 0:
            return True
        else:
            return False

    def set_labor(self):
        self.array = []
        if self.weight < 0:  # もし重み（人が不足していたら）
            for id in self.can_work_labor_ids:
                for labor in labors:
                    try:
                        if int(labor.id) == int(id):
                            if (labor.is_weekly_limit_day()
                                and labor.is_daily_limit_day(id)
                                    and self.confirm_need()):
                                self.need = self.need - 1
                                self.array.append(id)
                                confirm_limitday(id)
                    except ValueError:
                        break
        else:
            id = select_sort_at_weekly_limit_day(self.can_work_labor_ids)
            for id in self.can_work_labor_ids:
                for labor in labors:
                    try:
                        if int(labor.id) == int(id):
                            if (labor.is_weekly_limit_day()
                                and labor.is_daily_limit_day(id)
                                    and self.confirm_need()):
                                self.need = self.need - 1
                                self.array.append(id)
                                confirm_limitday(id)
                    except ValueError:
                        break

        return self.array


class labor(object):
    def __init__(self, name, id, limit_week, limit_day):
        self.name = name
        self.id = id
        self.limit_week = limit_week
        self.limit_day = limit_day
        labors.append(self)

    def set_cell(self):
        self.limit_week = self.limit_week - 1
        self.limit_day = self.limit_day - 1

    def is_weekly_limit_day(self):
        if int(self.limit_week) != 0:
            return True
        else:
            return False

    def is_daily_limit_day(self, cell_id):
        cell_ids = search_cell_groupe_ids(cell_id)
        count = 0
        for id in cell_ids:  # cell_ids:ある日のセルのIDの集合
            for cell in cells:  # 確定したセルの集合
                if id in cell.labor_ids:  # labor_idsにidがおったらtrue
                    count += 1
        if count != self.limit_day:
            return True
        else:
            return False


def confirm_limitday(labor_id):
    for labor_data in labors:
        try:
            int(labor_id)
        except ValueError:
            break

        if int(labor_id) == int(labor_data.id):
            labor_data.set_cell()


def select_sort_at_weight(data):
    for i in range(len(data)):
        Min = i  # 入れ替え対象をセット
        for j in range(i+1, len(data)):
            # セットした値よりも小さな値があれば，その位置を最小値として記録
            if int(data[j].weight) < int(data[Min].weight):
                Min = j
    # いまの位置と最小値を入れ替え ⇒ 結果，左から小さい順に並ぶ
        data[i], data[Min] = data[Min], data[i]

    return data  # 並べ替えを終えたデータを返す


def select_sort_at_weekly_limit_day(id_list):
    data = []
    for id in id_list:
        for labor in labors:
            if id == labor.id:
                data.append()

    for i in range(len(data)):
        Min = i  # 入れ替え対象をセット
        for j in range(i+1, len(data)):
            # セットした値よりも小さな値があれば，その位置を最小値として記録
            if data[j].limit_week < data[Min].limit_week:
                Min = j
    # いまの位置と最小値を入れ替え ⇒ 結果，左から小さい順に並ぶ
        data[i], data[Min] = data[Min], data[i]

    data.reverse()

    sorted_id = []
    for labor_data in data:
        sorted_id.append(labor_data.id)

    return sorted_id  # 並べ替えを終えたデータを返す


def main():
    labor_data = pd.read_csv('labor_data.csv', encoding="shift-jis")
    labor_data.index = labor_data.index + 1
    for i in range(1, len(labor_data) + 1):
        data = labor(labor_data['UserName'][i], labor_data['UserID'][i],
                     labor_data['limit_week'][i], labor_data['limit_day'][i])

    cell_data = pd.read_csv('cell_data.csv', encoding="shift-jis")
    cell_data.index = cell_data.index + 1
    for i in range(1, len(cell_data) + 1):
        data = temp_cell(cell_data['Cell_ID'][i], cell_data['Need'][i],
                         cell_data['Can_work_labor_id'][i])
        data.calc_weight()

    sorted_temp_cells = select_sort_at_weight(temp_cells.copy())

    for array in sorted_temp_cells:
        Cell = cell(array.cell_id, array.set_labor(),
                    array.need)  # ここでセルを確定させている。
        print("セルID:", Cell.cell_id, "労働者ID", Cell.labor_id)

    print("---労働者名,ID、上限日数---")
    for data in labors:
        print("名前", data.name, "ID:", data.id, "週上限", data.limit_week)

    print("----確定後のセル-----")
    print("---セルID、不足人数---")
    for cell_a in cells:
        print("セルID:", cell_a.cell_id, "不足人数", cell_a.need)


if __name__ == '__main__':
    main()
