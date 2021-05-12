var editor; // use a global for the submit and return data rendering in the examples

$(document).ready(function() {
    editor = new $.fn.dataTable.Editor( {
        ajax: "../php/staff.php",
        table: "#example",
        fields: [ {
                label: "First name:",
                name: "first_name"
            }, {
                label: "Last name:",
                name: "last_name"
            }, {
                label: "Position:",
                name: "position"
            }, {
                label: "Office:",
                name: "office"
            }, {
                label: "Extension:",
                name: "extn"
            }, {
                label: "Start date:",
                name: "start_date",
                type: "datetime"
            }, {
                label: "Salary:",
                name: "salary"
            }
        ]
    } );

    $('#example').on( 'click', 'tbody td', function (e) {
        var index = $(this).index();

        if ( index === 1 ) {
            editor.bubble( this, ['first_name', 'last_name'], {
                title: 'Edit name:'
            } );
        }
        else if ( index === 2 ) {
            editor.bubble( this, {
                buttons: false
            } );
        }
        else if ( index === 3 ) {
            editor.bubble( this );
        }
        else if ( index === 4 ) {
            editor.bubble( this, {
                message: 'Date must be given in the format `yyyy-mm-dd`'
            } );
        }
        else if ( index === 5 ) {
            editor.bubble( this, {
                title: 'Edit salary',
                message: 'Enter an unformatted number in dollars ($)'
            } );
        }
    } );

    $('#example').DataTable( {
        dom: "Bfrtip",
        ajax: "../php/staff.php",
        columns: [
            {
                data: null,
                defaultContent: '',
                className: 'select-checkbox',
                orderable: false
            },
            { data: null, render: function ( data, type, row ) {
                // Combine the first and last names into a single table field
                return data.first_name+' '+data.last_name;
            } },
            { data: "position" },
            { data: "office" },
            { data: "start_date" },
            { data: "salary", render: $.fn.dataTable.render.number( ',', '.', 0, '$' ) }
        ],
        order: [ 1, 'asc' ],
        select: {
            style:    'os',
            selector: 'td:first-child'
        },
        buttons: [
            { extend: "create", editor: editor },
            { extend: "edit",   editor: editor },
            { extend: "remove", editor: editor }
        ]
    } );
} );
