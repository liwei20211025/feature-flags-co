import { Component, OnInit, TemplateRef, ViewChild } from '@angular/core';
import { NzMessageService } from 'ng-zorro-antd/message';
import { AccountService } from 'src/app/services/account.service';
import { AnalyticsService } from 'src/app/services/analytics.service';
import { uuidv4 } from 'src/app/utils';
import { NewReportComponent } from './components/new-report/new-report.component';
import { CalculationType, DataCard, dataSource, IDataCard, IDataItem, updataReportParam } from './types/analytics';
import * as moment from 'moment';
import { DataSourcesComponent } from './components/data-sources/data-sources.component';

@Component({
  selector: 'app-analytics',
  templateUrl: './analytics.component.html',
  styleUrls: ['./analytics.component.less']
})
export class AnalyticsComponent implements OnInit {

  //ranges = { 今天: [new Date(), new Date()], '本月': [new Date(), endOfMonth(new Date())] };
  listData: DataCard[] = [];
  isLoading = false;
  dataSourceModalVisible = false;

  public dataSourcesManageModalVisible = false;

  private analyticBoardId: string = "";
  private envID: number = null;

  public dataSourceList: dataSource[] = [];                 // 数据源列表
  public dataSourceBoardType: 'table' | 'form' = 'table';   // 添加数据源弹窗界面类型
  public dataSourceOperatorType: 'new' | 'edit' = 'new';    // 如何操作数据源
  public currentDataSource: dataSource;                     // 当前数据源

  public reportsForCurrDataSource: any[] = [];              // 当前将要被删除的数据源，被使用的报表列表

  @ViewChild("addDataSourceTem", {static: false}) addDataSoureTem: TemplateRef<any>;
  @ViewChild("dataSources", {static: false}) dataSourceCom: DataSourcesComponent;
  @ViewChild("newReport", {static: false}) newReportCom: NewReportComponent;

  constructor(
    private message: NzMessageService,
    private accountServe: AccountService,
    private analyticServe: AnalyticsService
  ) {

    // this.listData = new Array(3).fill({}).map((_, index) => new DataCard({
    //     id: `${index}`,
    //     name: `我的第 ${index} 个看板`,
    //     startTime: new Date(),
    //     endTime: new Date(),
    //     isLoading: true,
    //     items: new Array(6).fill({}).map((_i, index) => ({
    //       id: `${index}`,
    //       name: `Data item  ${index}`,
    //       value: parseFloat((Math.random() * 100).toFixed(2)),
    //       dataSource: 'sdf',
    //       unit: 'EUR',
    //       color: 'red',
    //       calculationType: CalculationType.Count
    //     }))
    //   })
    // );

    // TODO to be removed
    // setTimeout(() => this.listData.forEach(d => d.isLoading = false), 200);
  }

  ngOnInit(): void {
    this.initBoardData();
  }

  // 初始化看板数据
  private initBoardData() {
    const { projectEnv: {envId} } = this.accountServe.getCurrentAccountProjectEnv();

    this.analyticServe.getAnalyticBoardData(envId)
      .subscribe((result: {
        id: string;
        envId: number;
        dataSourceDefs: dataSource[],
        dataGroups: DataCard[]
      }) => {
        this.analyticBoardId = result.id;
        this.envID = result.envId;
        this.dataSourceList = result.dataSourceDefs;
        console.log(result)

        let groups = result.dataGroups;
        groups.forEach((group: DataCard) => {
          this.listData[this.listData.length] = new DataCard({...group, isLoading: false, isEditing: false, itemsCount: group.items.length});
        })

        this.requestValueForItems();
      })
  }

  // 设置每个 item 的 value 值
  private requestValueForItems() {

  }

  onDateChange(data: any){
    console.log('data changed');
  }

  // 切换看板状态
  public toggleEditingCard(card: IDataCard) {
    card.items = card.items.filter(i => i.name !== null && i.name !== '' && i.dataSource !== null);

    if(card.isEditing) {
      this.setSaveReportParam(card);
    } else {
      card.isEditing = true;
    }
  }

  // 设置保存报表参数
  private setSaveReportParam(card: IDataCard) {
    let param: updataReportParam = {
      analyticBoardId: this.analyticBoardId,
      envId: this.envID,
      id: card.id,
      name: card.name || null,
      items: card.items,
      startTime: card.startTime ? moment(card.startTime).format("YYYY-MM-DD") : null,
      endTime: card.endTime ? moment(card.endTime).format("YYYY-MM-DD") : null
    }
    this.onSaveReportData(param, card);
  }

  // 保存报表
  private onSaveReportData(param: updataReportParam, card: IDataCard) {
    this.analyticServe.saveReport(param)
      .subscribe((result) => {
        console.log(result);
        this.message.success("报表更新成功!");
        card.isEditing = false;
      })
  }

  onCreateCard() {
    const card = new DataCard();
    this.currentDataCard = card;
    this.onAddItem(card);
    this.listData = [card, ...this.listData];
  }

  onAddItem(data: DataCard) {
    data.items = [...data.items, {
        id: uuidv4(),
        name: null,
        value: null,
        dataSource: null,
        unit: null,
        color: null,
        calculationType: CalculationType.Count
    }]

    data.itemsCount = data.itemsCount + 1;
    console.log(data)
  }

  // 删除报表
  public removeCard(card: IDataCard) {
    this.analyticServe.deleteReport(this.envID, this.analyticBoardId, card.id)
      .subscribe(() => {
        const idx = this.listData.findIndex(d => d.id === card.id);
        idx > -1 && this.listData.splice(idx, 1);
        this.message.success("表报移除成功!");
      })
  }

  removeDataItem(card: DataCard, item: IDataItem) {
    const idx = card.items.findIndex(i => i.id === item.id);
    if (idx > -1) {
      card.items.splice(idx, 1);
      card.itemsCount = card.itemsCount - 1;
    }
  }

  currentDataItem: IDataItem = null;
  currentDataCard: DataCard = null;

  // 点击设置数据源（打开设置数据源弹窗）
  public onSetDataSource(card: DataCard, item: IDataItem) {
    this.currentDataItem = {...item};
    this.currentDataCard = card;
    this.dataSourceModalVisible = true;
  }

  // 切换数据源界面
  public onOperatorDataSource() {
    if(this.dataSourceBoardType === 'table') {
      this.currentDataSource = {
        id: uuidv4(),
        name: "",
        dataType: "数值"
      }

      this.dataSourceOperatorType = 'new';
      this.dataSourceBoardType = 'form';
    } else {
      this.onAddDataSource();
    }
  }

  // 操作取消按钮
  public onOperatorCancel() {
    if(this.dataSourceBoardType === 'table') {
      this.dataSourcesManageModalVisible = false;
    } else {
      this.dataSourceBoardType = "table";
    }
  }

  // 设置数据源
  public onApplyDataSource () {
    // let item = this.currentDataCard.items.find(i => i.id === this.currentDataItem.id);
    // if (item) {
    //   item = Object.assign({}, this.currentDataItem);
    // }
    console.log(this.currentDataItem);
    this.currentDataItem = {...this.currentDataItem, ...this.newReportCom.setParam()};
    this.currentDataCard.updateItem(this.currentDataItem);
    this.dataSourceModalVisible = false;
  }

  // 刷新页面
  public onRefreshPage() {

  }

  // 打开添加数据源弹窗
  public onOpenAddDataSoureModal() {
    this.dataSourcesManageModalVisible = true;
  }

  // 关闭添加数据源弹窗
  public onCloseAddDataSoureModal() {
    this.dataSourcesManageModalVisible = false;
  }

  // 返回表格界面
  public onReturnTable() {
    this.dataSourceBoardType = 'table';
  }

  // 确认添加数据源
  private onAddDataSource = () => {
    const dataSource: dataSource = this.dataSourceCom.setParam();
    const newDataSource = {
      analyticBoardId: this.analyticBoardId,
      envID: this.envID,
      id: dataSource.id,
      name: dataSource.name,
      dataType: dataSource.dataType
    }
    this.analyticServe.addDataSourece(newDataSource)
      .subscribe(() => {
        this.dataSourceOperatorType === 'new' && (this.dataSourceList[this.dataSourceList.length] = dataSource);
        this.dataSourceBoardType = "table";
      })
  }

  // 删除数据源
  public onDeleteDataSource(dataSource: dataSource) {
    // 检测是否有使用过该数据源的报表
    const isHas = this.findReportsForCurrentDataSource(dataSource);

    if(isHas) {
      this.onApplyDelete(dataSource);
    } else {
      // 显示使用当前数据源的报表
      this.reportsForCurrDataSource.forEach(report => {
        this.message.warning(`当前数据源正在被报表 “${report.name}” 的 “${report.itemName}” 项目使用！`)
      })
    }
  }

  // 查找正在使用当前数据源的报表
  private findReportsForCurrentDataSource(dataSource: dataSource): boolean {
    this.reportsForCurrDataSource = [];

    this.listData.forEach((data: DataCard) => {
      if(data.items.length) {
        data.items.forEach((item: IDataItem) => {
          if(item.dataSource.id === dataSource.id) {
            this.reportsForCurrDataSource[this.reportsForCurrDataSource.length] = {
              name: data.name,
              itemName: item.name
            };
          }
        })
      }
    })

    return this.reportsForCurrDataSource.length === 0;
  }

  // 执行删除
  private onApplyDelete(dataSource: dataSource) {
    this.analyticServe.deleteDateSource(this.envID, this.analyticBoardId, dataSource.id)
      .subscribe(() => {
        const index = this.dataSourceList.findIndex(data => data.id === dataSource.id);
        if(index !== -1) {
          this.dataSourceList.splice(index, 1);
          this.dataSourceList = [...this.dataSourceList];
        }
      })
  }
}

