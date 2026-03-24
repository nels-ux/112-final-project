%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int yylineno;
extern char* yytext;
void yyerror(const char *s);
int yylex();

/* Global Buffer to store the MIPS/Hex text until the end */
char technical_buffer[5000] = "";

void print_binary_to_buf(int n, char* buf) {
    for (int i = 31; i >= 0; i--) {
        sprintf(buf + strlen(buf), "%d", (n >> i) & 1);
        if (i % 8 == 0 && i != 0) sprintf(buf + strlen(buf), " ");
    }
}

/* Stores the proof in the buffer instead of printing immediately */
void buffer_technical_proof(const char* id, int val) {
    char temp[1000];
    sprintf(temp, "\n--- LOW-LEVEL ARCHITECTURE PROOF [%s] ---\n", id);
    sprintf(temp + strlen(temp), "MIPS Assembly:  li $t0, %d\n", val);
    sprintf(temp + strlen(temp), "Binary (32-bit): ");
    print_binary_to_buf(val, temp);
    sprintf(temp + strlen(temp), "\nHexadecimal:    0x%08X\n", val);
    sprintf(temp + strlen(temp), "------------------------------------------\n");
    strcat(technical_buffer, temp);
}

/* Symbol Table */
int symbol_table[100]; 
char* variable_names[100];
int var_count = 0;

int get_value(char* name) {
    for(int i=0; i<var_count; i++) {
        if(strcmp(variable_names[i], name) == 0) return symbol_table[i];
    }
    return 0;
}

void set_value(char* name, int val) {
    for(int i=0; i<var_count; i++) {
        if(strcmp(variable_names[i], name) == 0) {
            symbol_table[i] = val;
            return;
        }
    }
    variable_names[var_count] = strdup(name);
    symbol_table[var_count++] = val;
}
%}

%union {
    int num;
    char* id;
    char* str;
}

%token <num> NUMBER
%token <id> ID
%token <str> STRING
%token START END NUM_TYPE ESHOW ASSIGN SEMI COMMA LPAREN RPAREN LBRACE RBRACE
%token PLUS MINUS MULT DIV

%type <num> expr
%left PLUS MINUS
%left MULT DIV

%%
/* We print the [OUTPUT] first, then the buffer, then the success message */
program: START LBRACE stmt_list RBRACE END { 
            printf("%s", technical_buffer); 
            printf("\n>>> Execution Successful <<<\n"); 
         }
       ;

stmt_list: stmt stmt_list | ;

stmt: decl SEMI | assign SEMI | display SEMI | expr SEMI | SEMI | ;

decl: NUM_TYPE ID ASSIGN expr { 
        set_value($2, $4); 
        buffer_technical_proof($2, $4); 
    }
    | NUM_TYPE ID { set_value($2, 0); }
    ;

assign: ID ASSIGN expr { 
        set_value($1, $3); 
        buffer_technical_proof($1, $3);
    }
    ;

display: ESHOW LPAREN STRING RPAREN { 
            char *s = $3; s[strlen(s)-1] = '\0'; 
            printf("[OUTPUT]: %s\n", s+1); 
         }
       | ESHOW LPAREN STRING COMMA ID RPAREN { 
            char *s = $3; s[strlen(s)-1] = '\0'; 
            printf("[OUTPUT]: %s %d\n", s+1, get_value($5)); 
         }
       ;

expr: expr PLUS expr  { $$ = $1 + $3; }
    | expr MINUS expr { $$ = $1 - $3; }
    | expr MULT expr  { $$ = $1 * $3; }
    | expr DIV expr   { if($3 != 0) $$ = $1 / $3; else { yyerror("Div by zero"); $$ = 0; } }
    | LPAREN expr RPAREN { $$ = $2; }
    | NUMBER          { $$ = $1; }
    | ID              { $$ = get_value($1); }
    ;
%%

void yyerror(const char *s) {
    fprintf(stderr, "Error at line %d: %s near '%s'\n", yylineno, s, yytext);
}

int main() {
    return yyparse();
}