import { Component, OnInit, TemplateRef, ViewChild } from '@angular/core';
import { NzMessageService } from 'ng-zorro-antd/message';
import { NzModalService } from 'ng-zorro-antd/modal';
import { AccountService } from 'src/app/services/account.service';
import { AnalyticsService } from 'src/app/services/analytics.service';
import { uuidv4 } from 'src/app/utils';
import { formatDate } from 'src/app/utils/format-date';
import { NewDatasourceComponent } from './components/new-datasource/new-datasource.component';
import { NewReportComponent } from './components/new-report/new-report.component';
import { CalculationType, DataCard, dataSource, IDataCard, IDataItem, updataReportParam } from './types/analytics';

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

  private analyticBoardId: string = "";
  private envID: number = null;

  public dataSourceList: dataSource[] = [];       // 数据源列表

  @ViewChild("addDataSourceTem", {static: false}) addDataSoureTem: TemplateRef<any>;
  @ViewChild("newDataSource", {static: false}) newDataSourceCom: NewDatasourceComponent;
  @ViewChild("newReport", {static: false}) newReportCom: NewReportComponent;

  constructor(
    private message: NzMessageService,
    private modalServe: NzModalService,
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
        dataSourceDefs: dataSource[]
      }) => {
        this.analyticBoardId = result.id;
        this.envID = result.envId;
        this.dataSourceList = result.dataSourceDefs;
        console.log(result)
        console.log("dataSourceList：", this.dataSourceList)
      })
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
      startTime: card.startTime ? formatDate("YY-mm-dd", card.startTime) : null,
      endTime: card.endTime ? formatDate("YY-mm-dd", card.endTime) : null
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
  }

  removeCard(card: IDataCard) {
    const idx = this.listData.findIndex(d => d.id === card.id);
    if (idx > -1) {
      this.listData.splice(idx, 1);
    }
  }

  removeDataItem(card: DataCard, item: IDataItem) {
    const idx = card.items.findIndex(i => i.id === item.id);
    if (idx > -1) {
      card.items.splice(idx, 1)
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

  // 设置数据源
  onApplyDataSource () {
    // let item = this.currentDataCard.items.find(i => i.id === this.currentDataItem.id);
    // if (item) {
    //   item = Object.assign({}, this.currentDataItem);
    // }
    console.log(this.currentDataItem);
    this.currentDataItem = {...this.currentDataItem, ...this.newReportCom.setParam()};
    this.currentDataCard.updateItem(this.currentDataItem);
    this.dataSourceModalVisible = false;
  }

  // 打开添加数据源弹窗
  public onOpenAddDataSoureModal() {
    this.modalServe.create({
      nzTitle: "添加数据源",
      nzContent: this.addDataSoureTem,
      nzOnOk: this.onAddDataSource
    })
  }

  // 确认添加数据源
  private onAddDataSource = () => {
    const dataSource: dataSource = this.newDataSourceCom.setParam();
    const newDataSource = {
      analyticBoardId: this.analyticBoardId,
      envID: this.envID,
      dataSourceDefs: [...this.dataSourceList, dataSource]
    }
    this.analyticServe.addDataSourece(newDataSource)
      .subscribe(() => {
        this.dataSourceList[this.dataSourceList.length] = dataSource;
      })
  }
}

