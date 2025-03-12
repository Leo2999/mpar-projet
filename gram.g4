grammar gram;

program : defstates defactions? transitions EOF;

defstates : states_reward | states_no_reward;

states_reward : STATES state_reward_list SEMI;

state_reward_list : state_reward (VIRG state_reward)*;

state_reward : ID DPOINT INT;

states_no_reward : STATES state_list SEMI;

state_list : ID (VIRG ID)*;

defactions : ACTIONS ID (VIRG ID)* SEMI;

transitions : trans+;

trans : transact | transnoact;

transact : ID LCROCH ID RCROCH FLECHE INT DPOINT ID (PLUS INT DPOINT ID)* SEMI;

transnoact : ID FLECHE INT DPOINT ID (PLUS INT DPOINT ID)* SEMI;

// Lexer rules
STATES    : 'States';
ACTIONS   : 'Actions';
DPOINT    : ':';
FLECHE    : '->';
SEMI      : ';';
VIRG      : ',';
PLUS      : '+';
LCROCH    : '[';
RCROCH    : ']';

INT       : [0-9]+;
ID        : [a-zA-Z_][a-zA-Z_0-9]*;
WS        : [ \t\n\r\f]+ -> skip;