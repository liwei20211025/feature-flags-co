import { Component, Input, OnInit } from '@angular/core';
import { dataSource } from '../../types/analytics';
import { countMode } from '../../types/static';

@Component({
  selector: 'app-new-report',
  templateUrl: './new-report.component.html',
  styleUrls: ['./new-report.component.less']
})
export class NewReportComponent implements OnInit {

  @Input() dataSourceList: dataSource[] = [];

  public countMode = countMode;               // 计数方式
  public dataSource: dataSource;              // 数据源
  public unit: string = "";                   // 单位
  public calculationType = countMode[0].id;   // 选择计数方式
  public color: string = "#000000";           // 文字颜色

  constructor() { }

  ngOnInit(): void {
  }
  
  // 设置参数
  public setParam() {
    return {
      dataSource: this.dataSource,
      unit: this.unit,
      color: this.color,
      calculationType: this.calculationType
    }
  }
}
