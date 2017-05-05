BEGIN{ 
	a=0;
	b=0; 
	f1=""; 
	f3="";
	first=1; 
} 

{ 
	if( f1 == $1 ){
		a=0;
	}
	else {
		a=1;
		f1=$1;
	}

	if( f3 == $3 ){
		b=0;
	}
	else {
		b=1;
		f3=$3;
	}
	
	if( first !=1 )	{	
	if( a==1 ){ 
		printf ")\n%s\n\t%s ( %s ",$1,$3,$2;  
	}
	
	if( a==0 && b==1){
		printf ")\n\t%s ( %s ",$3,$2;
	}	

	if( a==0 && b==0){
		printf "%s ",$2;
	}
	}
	else {
		printf "%s\n\t%s ( %s ",$1,$3,$2;  
		first=0;
	}

}
