import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import { updataReportParam } from '../pages/main/analytics/types/analytics';

@Injectable({
  providedIn: "root"
})
export class AnalyticsService {

  baseUrl: string = environment.url + '/api/analytics';

  constructor(
    private http: HttpClient
  ) {}

  // 获取看板数据
  public getAnalyticBoardData(envID: number): Observable<any> {
    const url = `${this.baseUrl}/${envID}`;
    return this.http.get(url);
  }

  // 添加数据源
  public addDataSourece(param: any): Observable<any> {
    const url = `${this.baseUrl}/data-source`;
    return this.http.post(url, param)
  }

  // 保存报表
  public saveReport(param: updataReportParam): Observable<any> {
    const url = `${this.baseUrl}/data-group`;
    return this.http.post(url, param);
  }
}
