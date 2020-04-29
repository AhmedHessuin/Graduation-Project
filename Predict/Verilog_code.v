module Moudel_0( clk , INPUT , OUTPUT );
parameter
 	state_state_1 = 0 ,
  	state_state_2 = 1 ,
  	state_state_3 = 2 ,
  	state_state_4 = 3 ,
  	state_state_5 = 4 ;
input
	clk;
input INPUT;
output reg	 OUTPUT; reg state;

 initial	 state = state_state_1;

 always@ (posedge clk)

 case(state)
	state_state_1:
	begin
		if(INPUT == 1'b1)
		begin
			OUTPUT = 1'b1;
			state = state_state_1;
		end
		if(INPUT == 1'b1)
		begin
			OUTPUT = 1'b1;
			state = state_state_2;
		end
	end

	state_state_2:
	begin
		if(INPUT == 1'b0)
		begin
			OUTPUT = 1'b1;
			state = state_state_2;
		end
	end

	state_state_3:
	begin
		if(INPUT == 1'b0)
		begin
			OUTPUT = 1'b0;
			state = state_state_1;
		end
	end

	state_state_4:
	begin
		if(INPUT == 1'b1)
		begin
			OUTPUT = 1'b1;
			state = state_state_3;
		end
		if(INPUT == 1'b0)
		begin
			OUTPUT = 1'b0;
			state = state_state_5;
		end
		if(INPUT == 1'b1)
		begin
			OUTPUT = 1'b1;
			state = state_state_4;
		end
	end

	state_state_5:
	begin
		if(INPUT == 1'b1)
		begin
			OUTPUT = 1'b0;
			state = state_state_5;
		end
	end

 endcase
endmodule
