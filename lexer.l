%{
#include "parser.tab.h"
#include <string.h>
#include <stdlib.h>

/* Track line numbers for error reporting */
extern int yylineno;
%}

/* This option automatically updates yylineno every time a \n is seen */
%option yylineno

%%
"start"         { return START; }
"end"           { return END; }
"num"           { return NUM_TYPE; }
"eshow"         { return ESHOW; }

[0-9]+          { yylval.num = atoi(yytext); return NUMBER; }
[a-zA-Z_][a-zA-Z0-9_]* { yylval.id = strdup(yytext); return ID; }
\"[^\"]*\"      { yylval.str = strdup(yytext); return STRING; }

"="             { return ASSIGN; }
"+"             { return PLUS; }
"-"             { return MINUS; }
"*"             { return MULT; }
"/"             { return DIV; }
";"             { return SEMI; }
","             { return COMMA; }
"("             { return LPAREN; }
")"             { return RPAREN; }
"{"             { return LBRACE; }
"}"             { return RBRACE; }

[ \t\r]         ; /* Skip whitespace */
\n              ; /* Handled by yylineno option */

.               { fprintf(stderr, "Lexical Error at line %d: Unknown character '%s'\n", yylineno, yytext); }
%%

int yywrap() { return 1; }