#!/usr/bin/env sh
OUT="$HOME/.feed/out"
DIR="$HOME/.feed/feeds"
n=1

show_feed_list () {
	# $1 indicates dialog type, i.e. cheklist or menu
	local FEEDS=`ls $DIR | wc -w | awk '{print $1}'`
    local arg=""
	local type="$1"

    if [ $FEEDS -eq 0 ] ; then
        dialog --msgbox "No Subsciptions found." 10 50
        main
    fi
	
	local i=1
    while [ $i -le $FEEDS ] ; do
        if [ "$type" == "checklist" ] ; then
			arg="$arg \"`cat $DIR/feed-$i | sed -ne '1p'`\" \"`cat $DIR/feed-$i | sed -ne '2p'`\" \"off\""
    	else
			arg="$arg \"`cat $DIR/feed-$i | sed -ne '1p'`\" \"`cat $DIR/feed-$i | sed -ne '2p'`\""
		fi
		i=$(($i+1))
	done

    eval "dialog --title 'Update' --$type 'Choose subscriptions to update' 20 80 50 $arg" 2>$OUT
}

show_feed_menu () {
	local arg=""
	local total=$((`cat $DIR/feed-$1 | wc -l`/3 - 1))
    local j=1
	local k=4
	#echo "total: $total"
    while [ $j -le $total ] ; do
        arg="$arg $j \"`cat $DIR/feed-$1 | sed -ne "$k""p"`\""
		j=$(($j+1))
		k=$(($k+3))
		#echo "arg: $arg"
    done
	#echo "arg: $arg"
    eval "dialog --title 'Read' --menu 'Choose a subscription to read' 20 100 50 $arg" 2>$OUT
}

read_sub () {
	show_feed_list "menu"
	local OPT="`cat $OUT`"
    if [ -z "$OPT" ] ; then
        main
    else
        OPT="`echo $OPT | sed -e 's/"//g'`"
		local rss_n=$OPT
		if [ -z "`cat $DIR/feed-$rss_n | sed -ne '4p'`" ] ; then 
			dialog --title "Read" --msgbox "Please update this subscription first." 5 50
			main
		fi
		
		while [ 1 -eq 1 ] ; do  	
			show_feed_menu $rss_n
   			OPT="`cat $OUT`"
			if [ -z "$OPT" ] ; then
				break
    		else
				OPT="`echo $OPT | sed -e 's/"//g'`"
				OPT=$(($OPT*3+1))
				local x="============================================="
				local p1="`cat $DIR/feed-$rss_n | sed -ne "$OPT"'p'`"
				OPT=$(($OPT+1))
				local p2="`cat $DIR/feed-$rss_n | sed -ne "$OPT"'p'`"
				OPT=$(($OPT+1))
				local p3="`cat $DIR/feed-$rss_n | sed -ne "$OPT"'p' | sed 's/<.*>//g'`"
				local msg="`printf "%s\n%s\n%s\n%s\n%s\n%s\n%s" "$x" "$p1" "$x" "$p2" "$x" "$p3" "$x"`"
				dialog --msgbox "$msg" 30 80 
			fi
		done
		main
	fi
}

test_new () {
	local FILEPATH="$HOME/.feed/feeds/feed-$n"
    echo $n > $FILEPATH
    ./feed.py -u "$1" -t >> $FILEPATH
    echo "$1" >> $FILEPATH
    n=$((n+1))
}

new_sub () {
	dialog --title "Subscibe" --inputbox "Enter an URL" 10 80 2>$OUT
	local URL="`cat $OUT`" 
 	if [ -z "$URL" ] ; then
		dialog --msgbox "No input!" 5 50
		main
	else
		local FILEPATH="$HOME/.feed/feeds/feed-$n"
		echo $n > $FILEPATH
		./feed.py -u "$URL" -t >> $FILEPATH
		echo "$URL" >> $FILEPATH
		n=$((n+1))
		main
	fi 
	#w3m -S -no-graph -dump -T text/html $URL
}

del_sub () {
	show_feed_list "menu"
	local OPT="`cat $OUT`"
    if [ -z "$OPT" ] ; then
        dialog --title "Delete" --msgbox "No input!" 5 50
        main
    else
        OPT="`echo $OPT | sed -e 's/"//g'`"
		local bound=$(($n-1))
#		if [ $j -eq 1  ] ; then
#        	rm -f $DIR/*
#		elif [ $j -eq $OPT ] ; then
#			rm -f $DIR/feed-$j
#		else
			local k=$OPT
			local j=$(($k+1))
        	while [ $k -lt $bound ] ; do
           		mv $DIR/feed-$j $DIR/feed-$k
				sed -i '' -e "1 s/^.*$/$k/g" $DIR/feed-$k
            	j=$(($j+1))
            	k=$(($k+1))
        	done	
#        fi 

		n=$(($n-1))
		rm -f $DIR/feed-$n
        dialog --title "Delete" --msgbox "Subscriptions successfully deleted." 5 50
        #w3m -S -no-graph -dump -T text/html `cat $DIR/feed-$i | sed -ne "$index""p"` > $DIR/feed-$i$j
        main
    fi
}


update_sub () {
	show_feed_list "checklist"
	local OPT="`cat $OUT`"
	if [ -z "$OPT" ] ; then
		dialog --msgbox "No input!" 5 50
		main
	else
		OPT="`echo $OPT | sed -e 's/"//g'`"
		local totalcount=`echo $OPT | wc -w | awk '{print $1}'` 
		arg=""
		local i=1
		while [ $i -le $totalcount ] ; do
			local u=`printf "$%s" "$i"`
			local k=`echo $OPT | awk "{print $u}"`
			echo "k= $k"
			./feed.py -u `cat $DIR/feed-$k | sed -ne '3p'` -i >> $DIR/feed-$k
			i=$(($i+1))
			echo $((100*$i/($totalcount+1)))
		done |  dialog --title "Updating" --gauge "Please wait..." 10 50 
		sleep 1
		#dialog --title "Updating" --msgbox "Subscriptions successfully updated." 20 80	
		#w3m -S -no-graph -dump -T text/html `cat $DIR/feed-$i | sed -ne "$index""p"` > $DIR/feed-$i$j
		main
	fi 
}

main () {
	dialog --title "Main menu" --menu "Choose Action" 20 80 50 R "Read subscribed feeds" S "Subscribe new subsscription" D "Delete subscription" U "Update a subcription" Q "Byes~" 2>$OUT

	local OPT="`cat $OUT`"
	case $OPT in
		R)
			read_sub
			;;
		S)
			new_sub
			;;
		D)
			del_sub
			;;
		U)
			update_sub
			;;
		Q)
			exit 0
			;;
	esac
}

rm -rf $HOME/.feed
mkdir -p $HOME/.feed/feeds
welcome='
      ___           ___           ___        
     /\  \         /\  \         /\  \        
    /::\  \       /::\  \       /::\  \          
   /:/\:\  \     /:/\ \  \     /:/\ \  \        
  /::\~\:\  \   _\:\~\ \  \   _\:\~\ \  \      
 /:/\:\ \:\__\ /\ \:\ \ \__\ /\ \:\ \ \__\    
 \/_|::\/:/  / \:\ \:\ \/__/ \:\ \:\ \/__/   
    |:|::/  /   \:\ \:\__\    \:\ \:\__\    
    |:|\/__/     \:\/:/  /     \:\/:/  /   
    |:|  |        \::/  /       \::/  /   
     \|__|         \/__/         \/__/  
                                  


 _         _____ _          _ _   _____           _       _   
(_)       /  ___| |        | | | /  ___|         (_)     | |  
 _ _ __   \ `--.| |__   ___| | | \ `--.  ___ _ __ _ _ __ | |_ 
| | "_ \   `--. \ "_ \ / _ \ | |  `--. \/ __| "__| | "_ \| __|
| | | | | /\__/ / | | |  __/ | | /\__/ / (__| |  | | |_) | |_ 
|_|_| |_| \____/|_| |_|\___|_|_| \____/ \___|_|  |_| .__/ \__|
                                                   | |        
                                                   |_|        

'

dialog --no-collapse --ok-label "Let's get started!!" --msgbox "$welcome" 30 150
test_new 'http://feeds.bbci.co.uk/news/rss.xml'
test_new 'http://rss.slashdot.org/Slashdot/slashdot'
#test_new 'http://www.phoronix.com/rss.php'
#test_new 'http://www.36kr.com/feed/'
main


