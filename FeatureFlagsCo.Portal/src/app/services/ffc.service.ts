import { Injectable, Inject } from '@angular/core';
import { FFCJsClient } from 'ffc-js-client-sdk/esm';

@Injectable({
  providedIn: 'root'
})
export class FfcService {

  client = FFCJsClient;
  constructor() {
  }
}
