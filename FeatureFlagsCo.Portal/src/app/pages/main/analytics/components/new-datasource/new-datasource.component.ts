import { Component, OnInit } from '@angular/core';
import { uuidv4 } from 'src/app/utils';
import { dataSource } from '../../types/analytics';

@Component({
  selector: 'app-new-datasource',
  templateUrl: './new-datasource.component.html',
  styleUrls: ['./new-datasource.component.less']
})
export class NewDatasourceComponent implements OnInit {

  public datasourceName: string = "";
  public datasourceType: string = "数值";

  constructor() { }

  ngOnInit(): void {
  }

  // 设置参数
  public setParam(): dataSource {
    return {
      id: uuidv4(),
      name: this.datasourceName,
      dataType: this.datasourceType
    }
  }
}
