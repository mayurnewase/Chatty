import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable()
export class SeatService {

  constructor(public http : HttpClient) { }

  getSeats(){
  	return this.http.get(environment.ikyBackend + "seats/").toPromise();
  }

  saveSeats(seat_map){
  	return this.http.post(environment.ikyBackend + "seats/save", seat_map).toPromise();
  }

  updateSeats(seat_map){
  	return this.http.post(environment.ikyBackend + "seats/update", seat_map).toPromise();
  }

}
