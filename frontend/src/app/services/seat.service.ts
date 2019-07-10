import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable()
export class SeatService {

  constructor(public http : HttpClient) { }

  getSeats(id){
  	return this.http.get(environment.ikyBackend + "seats/"+id).toPromise();
  }

  saveSeats(seat_map, id){
  	return this.http.post(environment.ikyBackend + "seats/", {"id": id, "seat_map": seat_map}).toPromise();
  }

  updateSeats(seat_map){
  	return this.http.post(environment.ikyBackend + "seats/update", seat_map).toPromise();
  }

}
