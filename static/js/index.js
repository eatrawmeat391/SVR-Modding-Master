function string_to_html_element(string)
{
	// call: var html = string_to_html_element("<input type='text' class='abc'></input>");
	// usage: $(html).find('input');
	
	var html = new DOMParser().parseFromString(string, 'text/xml');
	return html;
}

String.prototype.formatUnicorn = String.prototype.formatUnicorn ||
function () {
    "use strict";
    var str = this.toString();
    if (arguments.length) {
        var t = typeof arguments[0];
        var key;
        var args = ("string" === t || "number" === t) ?
            Array.prototype.slice.call(arguments)
            : arguments[0];

        for (key in args) {
            str = str.replace(new RegExp("\\{" + key + "\\}", "gi"), args[key]);
        }
    }

    return str;
};

function format_pac_name(id, type=1)
{
	if (type == 1)
	{
		if (id < 0xff)
			return "%02X".sprintf(id);
		else
			return "%04X".sprintf(id);
	}
}

function set_data_event()
{
	$(".file_no").on('blur', function(){
		var old_file_no = $(this).data("file_no");
		var new_file_no = $(this).val();
		old_file_no = parseInt(old_file_no, 16);
		new_file_no = parseInt(new_file_no, 16);
		if (isNaN(old_file_no) || isNaN(new_file_no))
		{
			alert("Please be sure to enter a valid integer value");
			$(this).val(format_pac_name(old_file_no));			
		}
		else if (old_file_no != new_file_no)
		{
			var dt = $("#table_pac_info").DataTable();
			data = dt.rows().data();
			for (var i=0; i<data.length; i++)
			{
				var html = string_to_html_element(data[i][0]);
				var existing_file_no = parseInt($(html).find('input').data('file_no'), 16);
				if (existing_file_no == new_file_no)
				{
					alert("Slot %s already existed, cannot rename to that slot".sprintf(format_pac_name(new_file_no)));
					$(this).val(format_pac_name(old_file_no));			
					return;
				}				
			}
			//alert("Check pass, rename slot %s to slot %s".sprintf(format_pac_name(old_file_no), format_pac_name(new_file_no)));
			
			var this_clicked_element = this;
			
			$.ajax({
            url: 'rename_pac_slot/' + old_file_no + '/' + new_file_no,  
            type: 'POST',
            success:function(data){
                // success here
				
				var structured_data = JSON.parse(data);
				
				var status = structured_data['status'];
				var msg = structured_data['msg'];
				
				if (status == 'success')
				{
					$(this_clicked_element).val(format_pac_name(new_file_no));
					$(this_clicked_element).data("file_no", format_pac_name(new_file_no));
				}
				
				alert(msg);
            },
            cache: false,
            contentType: 'json',
            processData: false
        });
		
			
		}
		else if (old_file_no == new_file_no)
		{
			// does not do anything
			return;
		}
	
		
	});
}
$(document).ready(function() {
	 $.ajax({
            url: 'load_existing_pac/' ,  
            type: 'POST',
            success:function(data){
                // success here
				
				structured_data = JSON.parse(data);
				
				if (structured_data.length == 0) return;
				
				var dt = $("#table_pac_info").DataTable({
				bDestroy: true, bSort: false})
				
				for (i=0; i<structured_data.length; i++)
				{
					// format name 
					var file_no = structured_data[i][0];
				    file_no = format_pac_name(file_no);
					structured_data[i][0] = "<input type='text' style='width:60px; text-align:center;' class='file_no' data-file_no='%s' value='%s'/>".sprintf(file_no, file_no);
					
					action_icon = "";
					structured_data[i].push(action_icon);
					
					dt.row.add(structured_data[i]);
				};
				
				dt.draw();
				set_data_event();
				
            },
            cache: false,
            contentType: 'json',
            processData: false
        });
		
	 $('#open_pac_input').change(function(){ 
        var formData = new FormData(document.getElementById('pac_fileinfo'));
		var filename = document.getElementById('open_pac_input').value.split('\\')[2]
        $.ajax({
            url: 'open_pac/' + filename,  
            type: 'POST',
            data: formData,
            success:function(data){
                // success here
				structured_data = JSON.parse(data);
				
				if (structured_data.length == 0) return;
				
				var dt = $("#table_pac_info").DataTable({
				bDestroy: true, bSort: false})
				
				for (i=0; i<structured_data.length; i++)
				{
					// format name 
					var file_no = structured_data[i][0];
				    file_no = format_pac_name(file_no);
					structured_data[i][0] = "<input type='text' style='width:60px; text-align:center;' class='file_no' data-file_no='%s' value='%s'/>".sprintf(file_no, file_no);
					action_icon = "";
					structured_data[i].push(action_icon);
										
					dt.row.add(structured_data[i]);
				};
				
				dt.draw();
				set_data_event();
				
            },
            cache: false,
            contentType: 'application/octet-stream',
            processData: false
        });
    });
	
  }
);