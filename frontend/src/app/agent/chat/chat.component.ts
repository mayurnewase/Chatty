import { Component, OnInit, Input,AfterViewChecked, ElementRef, ViewChild } from '@angular/core';
import { ChatService } from '../../services/chat.service';
import { SeatService } from '../../services/seat.service';
import { FormBuilder, FormGroup } from '@angular/forms';
import { trigger,style,transition,animate,keyframes,query,stagger } from '@angular/animations';

@Component({
	// tslint:disable-next-line:component-selector
	selector: 'app-chat',
	templateUrl: './chat.component.html',
	styleUrls: ['./chat.component.scss'],
	animations: [

		trigger('listAnimation', [
			transition('* => *', [

				query(':enter', style({ opacity: 0 }), {optional: true}),

				query(':enter', stagger('500ms', [
					animate('.3s ease-in-out', keyframes([
						style({opacity: 0, offset: 0}),
						style({opacity: .5, offset: 0.5}),
						style({opacity: 1,  offset: 1.0}),
					]))]), {optional: true})
			])
		])
	]
})

//Seat Configs
//seatmap -> contain many mapObj(1 row config -> [row_label, all_seats])
//mapObj -> contain many seatObj(all seats config [key,status,seatNumber])

export class ChatComponent implements OnInit {
	chatInitial;
	chatCurrent;
	
	messages: Message[] = [];
	prettyChatCurrent;

	chatForm: FormGroup;
	chatFormFields: any;
	@ViewChild('scrollMe') private myScrollContainer: ElementRef;


	seatConfig: any;
	seatmap = []; 					//store all rows_config
	seatId :any;

	//Seat pre-configurations ids

	allFullSeatConfigId = "all_full";
	allEmptySeatConfigId = "all_empty";

	private seatChartConfig = {
		showRowsLabel : true,
		showRowWisePricing : false,
		newSeatNoForRow : true
	}
	
	private cart = {
		selectedSeats : [],
		seatstoStore : [],
		eventId : 0
	}

	constructor(
		public fb: FormBuilder,
		public chatService: ChatService,
		public seatService: SeatService) {

		this.chatFormFields = {
			input: [''],
		};
		this.chatForm = this.fb.group(this.chatFormFields);

	}

	ngOnInit() {

		//Get Seat Map
		this.seatService.getSeats(this.allFullSeatConfigId).then(
			(s: any) => {
				this.seatmap = s[0].all_seats;
				this.seatId = s[0]._id;
				//this.seatmap = [];
				console.log("Seat map inside service", s[0]);
			
			this.chatInitial = {
				'currentNode': '',
				'complete': null,
				'context': {},
				'parameters': [],
				'extractedParameters': {},
				'speechResponse': '',
				'intent': {},
				'input': 'init_conversation',
				'missingParameters': [],
				'seat_map' : this.seatmap
			};

			console.log("sending initial chat ", this.chatInitial);
			this.chatService.converse(this.chatInitial)
				.then((c: any) => {
					c.owner = 'chat';
					this.changeCurrent(c);
					this.render_bubbles(c)
				});

			//this.processSeatChart(this.seatConfig);
		});//getSeats closed
	} //on_init closed

public selectSeat( seatObject : any )
	{
		console.log( "Seat to block: " , seatObject );
		if(seatObject.status == "available")
		{
			seatObject.status = "booked";
		}
		else if( seatObject.status = "booked" )
		{
			seatObject.status = "available";
		}
		console.log("seatmap after book ",this.seatmap)
		
		//this.seatService.updateSeats(this.seatmap).then(
		//	(s: any) => {
		//		//this.ngOnInit();
				//Do not modify database for custom config
		//		console.log("Return from update service is ", s);
		//	});
	}

//Various seat configs

public seatConfigAllFull(){
	this.seatService.getSeats(this.allFullSeatConfigId).then(
		(s: any) => {
			this.seatmap = s[0].all_seats;
			this.seatId = s[0]._id;
			//this.seatmap = [];
			console.log("Seat map in seatConfigAllFull", s[0]);
		});
}

scrollToBottom(): void {
		try {
				this.myScrollContainer.nativeElement.scrollTop = this.myScrollContainer.nativeElement.scrollHeight;
		} catch(err) { }                 
}

	render_bubbles(c){
		c.speechResponse.forEach((item, index) => {
			if (index  == 0){
					this.add_to_messages(item,"chat")
			}else{
				setTimeout(()=>{
					this.add_to_messages(item,"chat")
				},500)
			}
	});
	}
	add_to_messages(message, author){
			let new_message = new Message(message,author)
			this.messages.push(new_message);
			setTimeout(()=>{
				this.scrollToBottom();
			},300)
			
	}
	
	changeCurrent(c) {
		c.date = new Date();
		this.chatCurrent = c;
		this.prettyChatCurrent = JSON ? JSON.stringify(c, null, '  ') : 'your browser doesnt support JSON so cant pretty print';
	}

	send() {
		const form = this.chatForm.value;
		const sendMessage = {
			... this.chatCurrent,
			input: form.input,
			owner: 'user',
			seat_map : this.seatmap
		};
		this.add_to_messages(form.input,"user")

		this.changeCurrent(sendMessage);
		this.chatService.converse(sendMessage)
			.then((c: any) => {
				console.log("second chat message to send", sendMessage);
				console.log("agent gave ", c)

				c.owner = 'chat';
				this.changeCurrent(c);
				this.chatForm.reset();
				//need to get agent response and update ui to booked seat
				this.seatmap = c.seat_map;

				setTimeout(
					()=>{
						this.render_bubbles(c);
					},1000
				)
				
			});
	}
}

export class Message {
	content: string;
	author: string;

	constructor(content: string, author: string){
		this.content = content;
		this.author = author;
	}
}
