import { Component } from '@angular/core';

import { AppService } from './services/app.service';

import { parseString } from 'xml2js';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'app';
  data;

  constructor (private app: AppService) {
    app.getContacts().subscribe((data: Object) => this.parseData(data));
  }

  parseData (d: Object) {
    parseString(d, (err, result) => {
      this.data = result.ListBucketResult.Contents;
      console.log(this.data);
      this.data = this.data.map(x => {
        x.Key = x.Key[0];
        return x;
      });
      console.log(this.data);
    });
  }
}
