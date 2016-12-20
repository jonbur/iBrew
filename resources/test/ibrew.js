// Command iBrew

function joke()                 { $.getJSON( '/api/joke/'); }
function version()              { $.getJSON( '/api/version/'); }
function devices()              { $.getJSON( '/api/devices/'); }
function messages()             { $.getJSON( '/api/messages/'); }


// Command iKettle 2.0
function green(ip)              { $.getJSON( '/api/' + ip + '/green'); }
function black(ip)              { $.getJSON( '/api/' + ip + '/black'); }
function white(ip)              { $.getJSON( '/api/' + ip + '/white'); }
function oelong(ip)             { $.getJSON( '/api/' + ip + '/oelong'); }
function calibrate(ip)          { $.getJSON( '/api/' + ip + '/calibrate'); }
function coffee(ip)             { $.getJSON( '/api/' + ip + '/cofee'); }
function milk(ip)               { $.getJSON( '/api/' + ip + '/milk'); }
function boi(ip)                { $.getJSON( '/api/' + ip + '/boil'); }
function base(ip)               { $.getJSON( '/api/' + ip + '/base'); }
function setbase(ip,base)       { $.getJSON( '/api/' + ip + '/base/' + base); }
function heat()                 { $.getJSON( '/api/' + ip + '/heat/'); }
function formula()              { $.getJSON( '/api/' + ip + '/formula/'); }
function heat_temp(temperature) { $.getJSON( '/api/' + ip + '/heat/' + temperature); }
function formula_temperature(temperature)           { $.getJSON( '/api/' + ip + '/formula/' + temperature); }
function heat_keepwarm(temperature,keepwarm)        { $.getJSON( '/api/' + ip + '/heat/' + temperature + '/' + keepwarm); }
function formula_keepwarm(temperature,keepwarm)     { $.getJSON( '/api/' + ip + '/formula/' + temperature + '/' + keepwarm); }



// Command iKettle 2.0 and Smarter Coffee
function cups(ip,cups)              { $.getJSON( '/api/' + ip + '/cups/' + cups); }
function weak(ip)                   { $.getJSON( '/api/' + ip + '/weak'); }
function medium(ip)                 { $.getJSON( '/api/' + ip + '/medium'); }
function strong(ip)                 { $.getJSON( '/api/' + ip + '/strong'); }
function filter(ip,state)           { $.getJSON( '/api/' + ip + '/filter'); }
function descale(ip)                { $.getJSON( '/api/' + ip + '/descale'); }
function hotplateon(ip,minutes)     { $.getJSON( '/api/' + ip + '/hotplate/on/' + minutes); }
function hotplateoff(ip)            { $.getJSON( '/api/' + ip + '/hotplate/off'); }
function brew(ip)                   { $.getJSON( '/api/' + ip + '/'); }
function carafeon(ip)               { $.getJSON( '/api/' + ip + '/carafe/on'); }
function carafeoff(ip)              { $.getJSON( '/api/' + ip + '/carafe/off'); }
function modecup(ip)                { $.getJSON( '/api/' + ip + '/mode/carafe/cup'); }
function modecarafe(ip)             { $.getJSON( '/api/' + ip + '/mode/carafe/carafe'); }

// Command iKettle 2.0 and Smarter Coffee
function start(ip)                  { $.getJSON( '/api/' + ip + '/start'); }
function stop(ip)                   { $.getJSON( '/api/' + ip + '/stop'); }
function status(ip)                 { $.getJSON( '/api/' + ip + '/status'); }
function defaultsettings(ip)        { $.getJSON( '/api/' + ip + '/default'); }
function settings(ip)               { $.getJSON( '/api/' + ip + '/settings'); }

// Network Command iKettle 2.0 and Smarter Coffee
function statistics(ip)             { $.getJSON( '/api/' + ip + '/statistics'); }
function leave(ip)                  { $.getJSON( '/api/' + ip + '/scan'); }
function scan(ip)                   { $.getJSON( '/api/' + ip + '/leave'); }
function join(ip)                   { $.getJSON( '/api/' + ip + '/join'); }
function block(ip)                  { $.getJSON( '/api/' + ip + '/'); }
function unblock(ip)                { $.getJSON( '/api/' + ip + '/'); }
function patch(ip)                  { $.getJSON( '/api/' + ip + '/'); }
function rules(ip)                  { $.getJSON( '/api/' + ip + '/'); }
function triggers(ip)               { $.getJSON( '/api/' + ip + '/'); }
function groups(ip)                 { $.getJSON( '/api/' + ip + '/'); }
function triggersadd(ip)            { $.getJSON( '/api/' + ip + '/'); }
function triggersdelete(ip)         { $.getJSON( '/api/' + ip + '/'); }
function grouptriggersdelete(ip)    { $.getJSON( '/api/' + ip + '/'); }
function grouptriggers(ip,group)    { $.getJSON( '/api/' + ip + '/triggers/' + group); }




