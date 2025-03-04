import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzSelectModule } from 'ng-zorro-antd/select';
import { FormsModule } from '@angular/forms';
import { NzInputModule } from 'ng-zorro-antd/input';
import { NzSliderModule } from 'ng-zorro-antd/slider';
import { NzPaginationModule } from 'ng-zorro-antd/pagination';

import { NavBtnsComponent } from './nav-btns/nav-btns.component';
import { LayoutComponent } from './layout/layout.component';
import { UpperSwitchComponent } from './upper-switch/upper-switch.component';
import { TargetUserComponent } from './target-user/target-user.component';
import { FindRuleComponent } from './find-rule/find-rule.component';
import { RuleComponent } from './find-rule/rule/rule.component';
import { ServeComponent } from './find-rule/serve/serve.component';
import { ServeMultistatesComponent } from './find-rule/serve-multistates/serve-multistates.component';
import { FlagTriggersComponent } from './flag-triggers/flag-triggers.component';
import { ExperimentComponent } from './experiment/experiment.component';
import { NzPopconfirmModule } from 'ng-zorro-antd/popconfirm';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzDropDownModule } from 'ng-zorro-antd/dropdown';
import { NzAvatarModule } from 'ng-zorro-antd/avatar';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { NzModalModule } from 'ng-zorro-antd/modal';
import { NzTypographyModule } from 'ng-zorro-antd/typography';
import { NzDividerModule } from 'ng-zorro-antd/divider';
import { NzSpinModule } from 'ng-zorro-antd/spin';
import { NzToolTipModule } from 'ng-zorro-antd/tooltip';
import { NzTableModule } from 'ng-zorro-antd/table';
import {NzTabsModule} from "ng-zorro-antd/tabs";
import {NzSwitchModule} from "ng-zorro-antd/switch";
import {NzCollapseModule} from "ng-zorro-antd/collapse";


@NgModule({
  declarations: [
    NavBtnsComponent,
    LayoutComponent,
    UpperSwitchComponent,
    TargetUserComponent,
    FindRuleComponent,
    RuleComponent,
    ServeComponent ,
    ServeMultistatesComponent,
    FlagTriggersComponent,
    ExperimentComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    NzButtonModule,
    NzIconModule,
    NzInputModule,
    NzSelectModule,
    NzSliderModule,
    NzPaginationModule,
    NzPopconfirmModule,
    NzCardModule,
    NzDropDownModule,
    NzAvatarModule,
    NzTagModule,
    NzModalModule,
    NzTypographyModule,
    NzDividerModule,
    NzSpinModule,
    NzToolTipModule,
    NzTabsModule,
    NzSwitchModule,
    NzTableModule,
    NzCollapseModule
  ],
  exports: [
    NavBtnsComponent,
    LayoutComponent,
    CommonModule,
    UpperSwitchComponent,
    TargetUserComponent,
    FindRuleComponent,
    ServeComponent,
    ServeMultistatesComponent,
    FlagTriggersComponent,
    ExperimentComponent
  ]
})
export class ComponentsModule { }
