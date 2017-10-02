import { Injectable } from '@angular/core';
import { Http, Response } from '@angular/http';
import { Observable } from 'rxjs/Rx';
// import { User } from "app/models/user";

import { parseString } from 'xml2js';
 
@Injectable()
export class AppService {
   constructor(private http: Http) {
   }

   getContacts(): Observable<string> {
    return this.http.get('http://s3.amazonaws.com/subitup-calendars/?list-type=2')
        .map((res: Response) => res.text())
        .catch((error: any) => Observable.throw(error.json().error || 'Server error'));
   }
}
