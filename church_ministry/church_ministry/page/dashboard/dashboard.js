frappe.pages['dashboard'].on_page_load = function(wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Dashboard',
		single_column: true
	});
	$("<div class='chart_div' id='meter1' style='padding: 5px;display: inline-block;'></div>\
	   <div class='meter2' id='meter2' style='padding: 5px;display: inline-block;'></div>\
		<div class='meter3' id='meter3' style='padding: 5px;display: inline-block;'></div>\
		<div class='meter4' id='meter4' style='padding: 5px;display: inline-block;'></div>\
		<div class='meter5' id='meter5' style='padding: 5px;display: inline-block;'></div>").appendTo($(wrapper).find('.layout-main-section'));
	$("<table class='table table-bordered' style='height:350px;'padding: 15px; width:100%;'>\
	<tr width='100%'>\
	<td width='25%'><div class='c1' id ='i1'></div></td>\
	<td width='50%' rowspan='2'><div class='c2' id ='i2'>c2</div></td>\
	<td width='25%' rowspan='2'><div class='c3' id ='i3'>c3</div></td>\
	</tr>\
  <tr width='100%'>\
  <td width='25%'><div class='c4'  id ='i4'></div></td>\
  </tr>\
	</table>").appendTo($(wrapper).find('.layout-main-section'));
	new frappe.assign(wrapper);

}	

frappe.assign = Class.extend({
	init: function(wrapper) {
		this.wrapper = wrapper;
		this.body = $(this.wrapper).find(".assignt");
		this.setup_page();
		this.revenue_details();
    this.todo_details();
    this.event_details();
	},
	setup_page: function(ftv){
		var me = this;
		$(me.wrapper).find('.assignr').empty();	 
    frappe.call({
      method:"church_ministry.church_ministry.page.dashboard.dashboard.get_meter",
      callback: function(r) {
        var member=r.message.result.members[0][0];
        var ftvch=r.message.result.ftvch[0][0];
        var ftvcl=r.message.result.ftvcl[0][0];
        var nccl=r.message.result.nccl[0][0];
        var ncch=r.message.result.ncch[0][0];

        var options = {
          width: 175, height: 175,
          redFrom: 0, redTo: 2,
          yellowFrom:2, yellowTo: 5,
          minorTicks: 5,
          min:0,
          max:10
        };
        var data = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['Total Members', member],
        ]);
        var chart = new google.visualization.Gauge(document.getElementById('meter1'));
        chart.draw(data, options);

        var options = {
          width: 175, height: 175,
          redFrom: 0, redTo: 2,
          yellowFrom:2, yellowTo: 5,
          minorTicks: 5,
          min:0,
          max:10
        };
        var data = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['FTV (Cell)', ftvcl],
        ]);
        var chart = new google.visualization.Gauge(document.getElementById('meter2'));
        chart.draw(data, options);

        var options = {
          width: 175, height: 175,
          redFrom: 0, redTo: 2,
          yellowFrom:2, yellowTo: 5,
          minorTicks: 5,
          min:0,
          max:10
        };
        var data = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['FTV (Church)', ftvch],
        ]);
        var chart = new google.visualization.Gauge(document.getElementById('meter3'));
        chart.draw(data, options);

        var options = {
          width: 175, height: 175,
          redFrom: 0, redTo: 2,
          yellowFrom:2, yellowTo: 5,
          minorTicks: 5,
          min:0,
          max:10
        };
        var data = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['New Converts (CL.)', nccl],
        ]);
        mt='meter4'
        var chart = new google.visualization.Gauge(document.getElementById(mt));
        chart.draw(data, options);

        var options = {
          width: 175, height: 175,
          redFrom: 0, redTo: 2,
          yellowFrom:2, yellowTo: 5,
          minorTicks: 5,
          min:0,
          max:10
        };
        var data = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['New Converts (CH.)', ncch],
        ]);
        var chart = new google.visualization.Gauge(document.getElementById('meter5'));
        chart.draw(data, options);
      }
    });

        // table for My details
        $("<h4>Portal</h4><table class='table table-bordered' style='padding: 5px; width:100%;'>\
        	<tr width='100%'><td colspan='1'><a href='desk#Form/User/Administrator'><font color='blue'><u>My Profile</u></a></td></tr><tr width='100%'>\
          <td colspan='2'><a href='desk#List/Cell%20Meeting%20Invitation'><font color='blue'><u>My Cell Meeting's</u></a></td></tr>\
        	<tr width='100%'><td colspan='2'><a href='desk#List/Cell%20Meeting%20Invitation'><font color='blue'><u>My Church Meeting's</u></a></td></tr>\
        	</table>").appendTo($(me.wrapper).find('.c1'));
        $(me.wrapper).find('.c1').animate({  width: "100%", opacity: 1.5, fontSize: "1em",  borderWidth: "10px"  }, 1000 );
        $(me.wrapper).find('.c2').animate({  width: "100%", opacity: 1.5, fontSize: "1em",  borderWidth: "10px"  }, 1000 );
        $(me.wrapper).find('.c3').animate({  width: "100%", opacity: 1.5, fontSize: "1em",  borderWidth: "10px"  }, 1000 );
        $(me.wrapper).find('.c4').animate({  width: "100%", opacity: 1.5, fontSize: "1em",  borderWidth: "10px"  }, 1000 );
        $(me.wrapper).find('.c5').animate({  width: "100%", opacity: 1.5, fontSize: "1em",  borderWidth: "10px"  }, 1000 );
		
	} ,

	revenue_details:function(){
		  frappe.call({
			method:"church_ministry.church_ministry.page.dashboard.dashboard.get_revenue",
			callback: function(r) {
			var options = {packages: ['corechart'], callback : drawChart};
		    google.load('visualization', '1', options);
		    function drawChart() {
		  	mydata=[['Month','Donation','Pledge']];
		   	 for(var x in r.message.get_revenue){
  				mydata.push(r.message.get_revenue[x]);
               }
		    var data = google.visualization.arrayToDataTable(mydata);
		    var options = {
		      title: 'Revenue Details',
		      hAxis: {title: 'Month-Year', titleTextStyle: {color: 'black'}},
		      vAxis: {title: 'Revenue ',minValue:0,titleTextStyle: {color: 'black'}},
		      width: 600,
        	height:400,
        	legend: { position: 'top', maxLines: 3 }
		    };
		    var chart = new google.visualization.ColumnChart(document.getElementById('i2'));
		    chart.draw(data, options);
		  		}
		    }
	    });
	 },
   todo_details:function(){
      frappe.call({
        method:"church_ministry.church_ministry.page.dashboard.dashboard.get_todo",
        callback: function(r) {
        mydata=["<h4>ToDo's</h4><table cellspacing='10'>"];
        for(i=0;i<r.message.get_todo.length;i++) {
            str="<tr><td ><p><a href='desk#Form/ToDo/"+r.message.get_todo[i][0]+"'><font color='green'>"+r.message.get_todo[i][3]+"</font>&nbsp;&nbsp;&nbsp;</a> </td><td> "+r.message.get_todo[i][1]+"&nbsp;&nbsp;&nbsp;</td><td>"+r.message.get_todo[i][2]+"</p></tr>";
            mydata.push(str);
        } 
        $('.c3').html(mydata);
      }
      });
    
   },
   event_details:function(){
      frappe.call({
        method:"church_ministry.church_ministry.page.dashboard.dashboard.get_event",
        callback: function(r) {
        mydata=["<h4>My Events's</h4><table cellspacing='10' style='padding: 5px; width:100%;'>"];
        for(i=0;i<r.message.get_event.length;i++) {
            str="<tr><td width='100%'><p><a href='desk#Form/Event/"+r.message.get_event[i][0]+"'><font color='green'>"+r.message.get_event[i][1]+"</font></a></td></p></tr>";
            mydata.push(str);
        }
        mydata.push("<tr><td align='right'><p><a href='desk#List/Event'><font color='black'>...More</font></a></td></tr>");
        $('.c4').html(mydata);
      }
      });
   }

});
  




