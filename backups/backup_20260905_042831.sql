--
-- PostgreSQL database dump
--

\restrict 91tjqtcIMKyQsgnvxQUCcXNinwyJlMnjT4BUJIBH9SxhXo1yVK6zJOz4921Nsc7

-- Dumped from database version 17.11
-- Dumped by pg_dump version 17.11

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: academic_years; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.academic_years (
    id integer NOT NULL,
    year_name_gregorian character varying(20) NOT NULL,
    year_name_hijri character varying(20) NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    is_current boolean NOT NULL,
    status character varying(20) NOT NULL,
    is_closed boolean NOT NULL,
    closed_at timestamp without time zone,
    closed_by_user_id integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    CONSTRAINT ck_academic_years_status CHECK (((status)::text = ANY ((ARRAY['current'::character varying, 'closed'::character varying, 'upcoming'::character varying])::text[])))
);


ALTER TABLE public.academic_years OWNER TO postgres;

--
-- Name: academic_years_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.academic_years_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.academic_years_id_seq OWNER TO postgres;

--
-- Name: academic_years_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.academic_years_id_seq OWNED BY public.academic_years.id;


--
-- Name: annual_closing_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.annual_closing_logs (
    id integer NOT NULL,
    from_academic_year_id integer NOT NULL,
    to_academic_year_id integer NOT NULL,
    total_students_promoted integer NOT NULL,
    total_debts_carried_over numeric(12,2) NOT NULL,
    executed_by_user_id integer NOT NULL,
    execution_date timestamp without time zone DEFAULT now() NOT NULL,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.annual_closing_logs OWNER TO postgres;

--
-- Name: annual_closing_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.annual_closing_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.annual_closing_logs_id_seq OWNER TO postgres;

--
-- Name: annual_closing_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.annual_closing_logs_id_seq OWNED BY public.annual_closing_logs.id;


--
-- Name: backup_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.backup_logs (
    id integer NOT NULL,
    file_name character varying(255) NOT NULL,
    file_size character varying(50),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    created_by_user_id integer,
    updated_at timestamp without time zone
);


ALTER TABLE public.backup_logs OWNER TO postgres;

--
-- Name: backup_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.backup_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.backup_logs_id_seq OWNER TO postgres;

--
-- Name: backup_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.backup_logs_id_seq OWNED BY public.backup_logs.id;


--
-- Name: behavioral_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.behavioral_records (
    id integer NOT NULL,
    student_id integer NOT NULL,
    academic_year_id integer NOT NULL,
    behavior_type character varying(30) NOT NULL,
    title character varying(150) NOT NULL,
    details text,
    action_taken text,
    record_date date NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    CONSTRAINT ck_behavioral_records_type CHECK (((behavior_type)::text = ANY ((ARRAY['تميز'::character varying, 'مخالفة'::character varying, 'تنبيه أخصائي'::character varying])::text[])))
);


ALTER TABLE public.behavioral_records OWNER TO postgres;

--
-- Name: behavioral_records_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.behavioral_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.behavioral_records_id_seq OWNER TO postgres;

--
-- Name: behavioral_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.behavioral_records_id_seq OWNED BY public.behavioral_records.id;


--
-- Name: daily_attendance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.daily_attendance (
    id integer NOT NULL,
    student_id integer NOT NULL,
    academic_year_id integer NOT NULL,
    grade_id integer NOT NULL,
    section_id integer NOT NULL,
    attendance_date date NOT NULL,
    status character varying(20) NOT NULL,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    CONSTRAINT ck_daily_attendance_status CHECK (((status)::text = ANY ((ARRAY['حاضر'::character varying, 'غائب'::character varying, 'متأخر'::character varying, 'غائب بمبرر'::character varying])::text[])))
);


ALTER TABLE public.daily_attendance OWNER TO postgres;

--
-- Name: daily_attendance_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.daily_attendance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.daily_attendance_id_seq OWNER TO postgres;

--
-- Name: daily_attendance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.daily_attendance_id_seq OWNED BY public.daily_attendance.id;


--
-- Name: employee_allowances_deductions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employee_allowances_deductions (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    type character varying(20) NOT NULL,
    amount numeric(10,2) NOT NULL,
    reason text,
    date date NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    CONSTRAINT ck_employee_allowances_type CHECK (((type)::text = ANY ((ARRAY['بدل'::character varying, 'حافز'::character varying, 'مكافأة'::character varying, 'خصم'::character varying, 'غياب'::character varying])::text[])))
);


ALTER TABLE public.employee_allowances_deductions OWNER TO postgres;

--
-- Name: employee_allowances_deductions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.employee_allowances_deductions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.employee_allowances_deductions_id_seq OWNER TO postgres;

--
-- Name: employee_allowances_deductions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.employee_allowances_deductions_id_seq OWNED BY public.employee_allowances_deductions.id;


--
-- Name: employee_loans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employee_loans (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    total_loan_amount numeric(10,2) NOT NULL,
    monthly_deduction numeric(10,2) NOT NULL,
    status character varying(20) NOT NULL,
    loan_date date NOT NULL,
    reason text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    remaining_amount numeric(10,2) DEFAULT 0.00,
    CONSTRAINT ck_employee_loans_status CHECK (((status)::text = ANY ((ARRAY['مستمرة'::character varying, 'منتهية'::character varying])::text[])))
);


ALTER TABLE public.employee_loans OWNER TO postgres;

--
-- Name: employee_loans_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.employee_loans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.employee_loans_id_seq OWNER TO postgres;

--
-- Name: employee_loans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.employee_loans_id_seq OWNED BY public.employee_loans.id;


--
-- Name: employees; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employees (
    id integer NOT NULL,
    full_name character varying(150) NOT NULL,
    job_title character varying(100) NOT NULL,
    qualification character varying(100),
    primary_phone character varying(20),
    secondary_phone character varying(20),
    gender character varying(10),
    marital_status character varying(20),
    address character varying(20),
    status character varying(20) NOT NULL,
    national_id character varying(50),
    id_issue_place character varying(50),
    id_issue_date date,
    birth_date date,
    birth_village character varying(50),
    birth_district character varying(50),
    birth_governorate character varying(50),
    contract_start_date date,
    contract_end_date date,
    basic_salary numeric(10,2) NOT NULL,
    payment_method character varying(30) NOT NULL,
    bank_account_number character varying(50),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    CONSTRAINT ck_employees_gender CHECK (((gender)::text = ANY ((ARRAY['ذكر'::character varying, 'أنثى'::character varying])::text[]))),
    CONSTRAINT ck_employees_payment_method CHECK (((payment_method)::text = ANY ((ARRAY['حساب بنكي'::character varying, 'محفظة إلكترونية'::character varying, 'نقداً'::character varying])::text[]))),
    CONSTRAINT ck_employees_status CHECK (((status)::text = ANY ((ARRAY['نشط'::character varying, 'إجازة'::character varying, 'مستقيل'::character varying])::text[])))
);


ALTER TABLE public.employees OWNER TO postgres;

--
-- Name: employees_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.employees_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.employees_id_seq OWNER TO postgres;

--
-- Name: employees_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.employees_id_seq OWNED BY public.employees.id;


--
-- Name: expense_vouchers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expense_vouchers (
    id integer NOT NULL,
    voucher_number character varying(50) NOT NULL,
    expense_category character varying(50) NOT NULL,
    beneficiary_name character varying(150) NOT NULL,
    amount numeric(10,2) NOT NULL,
    payment_date timestamp without time zone DEFAULT now() NOT NULL,
    payment_method character varying(30) NOT NULL,
    invoice_number character varying(100),
    notes text,
    created_by_user_id integer NOT NULL,
    status character varying(20) NOT NULL,
    cancellation_reason text,
    cancelled_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    CONSTRAINT ck_expense_vouchers_category CHECK (((expense_category)::text = ANY ((ARRAY['مشتريات مواد'::character varying, 'صيانة وتشغيل'::character varying, 'فعاليات واحتفالات'::character varying, 'أنشطة مدرسية'::character varying, 'أخرى'::character varying])::text[]))),
    CONSTRAINT ck_expense_vouchers_payment_method CHECK (((payment_method)::text = ANY ((ARRAY['نقداً'::character varying, 'تحويل بنكي'::character varying, 'كريمي/حاسب'::character varying, 'شيك'::character varying])::text[]))),
    CONSTRAINT ck_expense_vouchers_status CHECK (((status)::text = ANY ((ARRAY['نشط'::character varying, 'ملغى'::character varying])::text[])))
);


ALTER TABLE public.expense_vouchers OWNER TO postgres;

--
-- Name: expense_vouchers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.expense_vouchers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.expense_vouchers_id_seq OWNER TO postgres;

--
-- Name: expense_vouchers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.expense_vouchers_id_seq OWNED BY public.expense_vouchers.id;


--
-- Name: fee_installments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fee_installments (
    id integer NOT NULL,
    student_fee_id integer NOT NULL,
    installment_type character varying(20) NOT NULL,
    installment_number integer NOT NULL,
    installment_name character varying(100) NOT NULL,
    amount numeric(10,2) NOT NULL,
    due_date date NOT NULL,
    is_paid boolean NOT NULL,
    paid_amount numeric(10,2) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    CONSTRAINT ck_fee_installments_type CHECK (((installment_type)::text = ANY ((ARRAY['previous_debt'::character varying, 'regular'::character varying])::text[])))
);


ALTER TABLE public.fee_installments OWNER TO postgres;

--
-- Name: fee_installments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fee_installments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fee_installments_id_seq OWNER TO postgres;

--
-- Name: fee_installments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fee_installments_id_seq OWNED BY public.fee_installments.id;


--
-- Name: fee_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fee_types (
    id integer NOT NULL,
    fee_name character varying(50) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.fee_types OWNER TO postgres;

--
-- Name: fee_types_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fee_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fee_types_id_seq OWNER TO postgres;

--
-- Name: fee_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fee_types_id_seq OWNED BY public.fee_types.id;


--
-- Name: final_exam_schedules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.final_exam_schedules (
    id integer NOT NULL,
    academic_year_id integer NOT NULL,
    term integer NOT NULL,
    grade_id integer NOT NULL,
    subject_id integer NOT NULL,
    exam_date date NOT NULL,
    day_name character varying(20) NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    CONSTRAINT ck_final_exam_term CHECK ((term = ANY (ARRAY[1, 2])))
);


ALTER TABLE public.final_exam_schedules OWNER TO postgres;

--
-- Name: final_exam_schedules_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.final_exam_schedules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.final_exam_schedules_id_seq OWNER TO postgres;

--
-- Name: final_exam_schedules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.final_exam_schedules_id_seq OWNED BY public.final_exam_schedules.id;


--
-- Name: grade_fee_structures; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grade_fee_structures (
    id integer NOT NULL,
    academic_year_id integer NOT NULL,
    grade_id integer NOT NULL,
    fee_type_id integer NOT NULL,
    amount numeric(10,2) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.grade_fee_structures OWNER TO postgres;

--
-- Name: grade_fee_structures_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.grade_fee_structures_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.grade_fee_structures_id_seq OWNER TO postgres;

--
-- Name: grade_fee_structures_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.grade_fee_structures_id_seq OWNED BY public.grade_fee_structures.id;


--
-- Name: grades; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grades (
    id integer NOT NULL,
    grade_name character varying(50) NOT NULL,
    stage_name character varying(50) NOT NULL,
    max_capacity integer NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.grades OWNER TO postgres;

--
-- Name: grades_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.grades_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.grades_id_seq OWNER TO postgres;

--
-- Name: grades_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.grades_id_seq OWNED BY public.grades.id;


--
-- Name: homeworks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.homeworks (
    id integer NOT NULL,
    academic_year_id integer NOT NULL,
    grade_id integer NOT NULL,
    section_id integer NOT NULL,
    subject_id integer NOT NULL,
    homework_date date NOT NULL,
    title character varying(150) NOT NULL,
    description text,
    due_date date NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.homeworks OWNER TO postgres;

--
-- Name: homeworks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.homeworks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.homeworks_id_seq OWNER TO postgres;

--
-- Name: homeworks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.homeworks_id_seq OWNED BY public.homeworks.id;


--
-- Name: import_export_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.import_export_logs (
    id integer NOT NULL,
    operation_type character varying(20) NOT NULL,
    entity_name character varying(50) NOT NULL,
    file_name character varying(255),
    executed_by integer,
    executed_at timestamp without time zone DEFAULT now() NOT NULL,
    status character varying(20) NOT NULL,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.import_export_logs OWNER TO postgres;

--
-- Name: import_export_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.import_export_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.import_export_logs_id_seq OWNER TO postgres;

--
-- Name: import_export_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.import_export_logs_id_seq OWNED BY public.import_export_logs.id;


--
-- Name: monthly_evaluations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.monthly_evaluations (
    id integer NOT NULL,
    student_id integer NOT NULL,
    academic_year_id integer NOT NULL,
    grade_id integer NOT NULL,
    section_id integer NOT NULL,
    subject_id integer NOT NULL,
    term integer NOT NULL,
    month integer NOT NULL,
    written_score numeric(5,2) NOT NULL,
    oral_score numeric(5,2) NOT NULL,
    homework_score numeric(5,2) NOT NULL,
    attendance_score numeric(5,2) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    CONSTRAINT ck_attendance_score_max CHECK ((attendance_score <= 20.00)),
    CONSTRAINT ck_homework_score_max CHECK ((homework_score <= 20.00)),
    CONSTRAINT ck_monthly_eval_month CHECK ((month = ANY (ARRAY[1, 2, 3]))),
    CONSTRAINT ck_monthly_eval_term CHECK ((term = ANY (ARRAY[1, 2]))),
    CONSTRAINT ck_oral_score_max CHECK ((oral_score <= 20.00)),
    CONSTRAINT ck_written_score_max CHECK ((written_score <= 40.00))
);


ALTER TABLE public.monthly_evaluations OWNER TO postgres;

--
-- Name: monthly_evaluations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.monthly_evaluations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.monthly_evaluations_id_seq OWNER TO postgres;

--
-- Name: monthly_evaluations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.monthly_evaluations_id_seq OWNED BY public.monthly_evaluations.id;


--
-- Name: monthly_exam_schedules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.monthly_exam_schedules (
    id integer NOT NULL,
    academic_year_id integer NOT NULL,
    term integer NOT NULL,
    month integer NOT NULL,
    grade_id integer NOT NULL,
    section_id integer,
    subject_id integer NOT NULL,
    exam_date date NOT NULL,
    day_name character varying(20) NOT NULL,
    period_number integer NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    CONSTRAINT ck_monthly_exam_month CHECK ((month = ANY (ARRAY[1, 2, 3]))),
    CONSTRAINT ck_monthly_exam_term CHECK ((term = ANY (ARRAY[1, 2])))
);


ALTER TABLE public.monthly_exam_schedules OWNER TO postgres;

--
-- Name: monthly_exam_schedules_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.monthly_exam_schedules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.monthly_exam_schedules_id_seq OWNER TO postgres;

--
-- Name: monthly_exam_schedules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.monthly_exam_schedules_id_seq OWNED BY public.monthly_exam_schedules.id;


--
-- Name: notification_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notification_logs (
    id integer NOT NULL,
    notification_id integer NOT NULL,
    parent_id integer NOT NULL,
    sent_at timestamp without time zone DEFAULT now() NOT NULL,
    delivery_status character varying(20) NOT NULL,
    read_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.notification_logs OWNER TO postgres;

--
-- Name: notification_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notification_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notification_logs_id_seq OWNER TO postgres;

--
-- Name: notification_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notification_logs_id_seq OWNED BY public.notification_logs.id;


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    title character varying(150) NOT NULL,
    message text NOT NULL,
    notification_type character varying(50) NOT NULL,
    sender_user_id integer,
    target_type character varying(30) NOT NULL,
    target_grade_id integer,
    target_section_id integer,
    scheduled_at timestamp without time zone,
    sent_at timestamp without time zone,
    is_active boolean NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.notifications OWNER TO postgres;

--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notifications_id_seq OWNER TO postgres;

--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- Name: parent_devices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.parent_devices (
    id integer NOT NULL,
    parent_id integer NOT NULL,
    device_token character varying(255) NOT NULL,
    device_type character varying(20),
    app_version character varying(30),
    last_login timestamp without time zone,
    is_active boolean NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    CONSTRAINT ck_parent_devices_type CHECK (((device_type)::text = ANY ((ARRAY['android'::character varying, 'ios'::character varying, 'web'::character varying])::text[])))
);


ALTER TABLE public.parent_devices OWNER TO postgres;

--
-- Name: parent_devices_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.parent_devices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.parent_devices_id_seq OWNER TO postgres;

--
-- Name: parent_devices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.parent_devices_id_seq OWNED BY public.parent_devices.id;


--
-- Name: parents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.parents (
    id integer NOT NULL,
    full_name character varying(150) NOT NULL,
    primary_phone character varying(20) NOT NULL,
    secondary_phone character varying(20),
    address text,
    job character varying(100),
    category character varying(20) NOT NULL,
    password_hash character varying(255) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    CONSTRAINT ck_parents_category CHECK (((category)::text = ANY ((ARRAY['عادي'::character varying, 'VIP'::character varying, 'كفالة'::character varying])::text[])))
);


ALTER TABLE public.parents OWNER TO postgres;

--
-- Name: parents_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.parents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.parents_id_seq OWNER TO postgres;

--
-- Name: parents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.parents_id_seq OWNED BY public.parents.id;


--
-- Name: payroll_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payroll_records (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    month integer NOT NULL,
    year integer NOT NULL,
    basic_salary numeric(10,2) NOT NULL,
    total_allowances numeric(10,2) NOT NULL,
    total_deductions numeric(10,2) NOT NULL,
    loan_deduction numeric(10,2) NOT NULL,
    net_salary numeric(10,2) NOT NULL,
    payment_status character varying(20) NOT NULL,
    payment_date timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    CONSTRAINT ck_payroll_month CHECK (((month >= 1) AND (month <= 12))),
    CONSTRAINT ck_payroll_status CHECK (((payment_status)::text = ANY ((ARRAY['مسلم'::character varying, 'معلق'::character varying])::text[])))
);


ALTER TABLE public.payroll_records OWNER TO postgres;

--
-- Name: payroll_records_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.payroll_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payroll_records_id_seq OWNER TO postgres;

--
-- Name: payroll_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.payroll_records_id_seq OWNED BY public.payroll_records.id;


--
-- Name: permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permissions (
    id integer NOT NULL,
    module_name character varying(50) NOT NULL,
    permission_key character varying(50) NOT NULL
);


ALTER TABLE public.permissions OWNER TO postgres;

--
-- Name: permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.permissions_id_seq OWNER TO postgres;

--
-- Name: permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.permissions_id_seq OWNED BY public.permissions.id;


--
-- Name: print_archive; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.print_archive (
    id integer NOT NULL,
    document_type character varying(50) NOT NULL,
    document_number character varying(100),
    related_record_id integer,
    printed_by integer,
    printed_at timestamp without time zone DEFAULT now() NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.print_archive OWNER TO postgres;

--
-- Name: print_archive_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.print_archive_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.print_archive_id_seq OWNER TO postgres;

--
-- Name: print_archive_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.print_archive_id_seq OWNED BY public.print_archive.id;


--
-- Name: receipts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.receipts (
    id integer NOT NULL,
    receipt_number character varying(50) NOT NULL,
    student_id integer NOT NULL,
    installment_id integer,
    payment_target character varying(30) NOT NULL,
    amount_paid numeric(10,2) NOT NULL,
    payment_date timestamp without time zone DEFAULT now() NOT NULL,
    payment_method character varying(30) NOT NULL,
    reference_number character varying(100),
    notes text,
    created_by_user_id integer NOT NULL,
    status character varying(20) NOT NULL,
    cancellation_reason text,
    cancelled_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    CONSTRAINT ck_receipts_payment_method CHECK (((payment_method)::text = ANY ((ARRAY['نقداً'::character varying, 'تحويل بنكي'::character varying, 'كريمي/حاسب'::character varying, 'شيك'::character varying])::text[]))),
    CONSTRAINT ck_receipts_payment_target CHECK (((payment_target)::text = ANY ((ARRAY['previous_debt'::character varying, 'current_fee'::character varying])::text[]))),
    CONSTRAINT ck_receipts_status CHECK (((status)::text = ANY ((ARRAY['نشط'::character varying, 'ملغى'::character varying])::text[])))
);


ALTER TABLE public.receipts OWNER TO postgres;

--
-- Name: receipts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.receipts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.receipts_id_seq OWNER TO postgres;

--
-- Name: receipts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.receipts_id_seq OWNED BY public.receipts.id;


--
-- Name: role_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.role_permissions (
    role_id integer NOT NULL,
    permission_id integer NOT NULL,
    can_view boolean NOT NULL,
    can_add boolean NOT NULL,
    can_edit boolean NOT NULL,
    can_delete boolean NOT NULL,
    can_print boolean NOT NULL,
    can_cancel boolean NOT NULL
);


ALTER TABLE public.role_permissions OWNER TO postgres;

--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    role_name character varying(50) NOT NULL,
    description text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: school_info; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.school_info (
    id integer NOT NULL,
    school_name_ar character varying(150) NOT NULL,
    school_name_en character varying(150),
    principal_name character varying(100),
    license_number character varying(50),
    phone_primary character varying(20),
    phone_secondary character varying(20),
    email character varying(100),
    address_detail text,
    logo_url character varying(255),
    header_footer_url character varying(255),
    terms_and_conditions text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.school_info OWNER TO postgres;

--
-- Name: school_info_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.school_info_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.school_info_id_seq OWNER TO postgres;

--
-- Name: school_info_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.school_info_id_seq OWNED BY public.school_info.id;


--
-- Name: sections; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sections (
    id integer NOT NULL,
    grade_id integer NOT NULL,
    section_name character varying(10) NOT NULL,
    capacity integer NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.sections OWNER TO postgres;

--
-- Name: sections_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sections_id_seq OWNER TO postgres;

--
-- Name: sections_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sections_id_seq OWNED BY public.sections.id;


--
-- Name: student_academic_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.student_academic_history (
    id integer NOT NULL,
    student_id integer NOT NULL,
    academic_year_id integer NOT NULL,
    grade_id integer NOT NULL,
    section_id integer NOT NULL,
    final_result character varying(20),
    promotion_status character varying(20),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    CONSTRAINT ck_student_history_promotion CHECK (((promotion_status)::text = ANY ((ARRAY['promoted'::character varying, 'retained'::character varying, 'withdrawn'::character varying])::text[]))),
    CONSTRAINT ck_student_history_result CHECK (((final_result)::text = ANY ((ARRAY['passed'::character varying, 'failed'::character varying, 'second_round'::character varying])::text[])))
);


ALTER TABLE public.student_academic_history OWNER TO postgres;

--
-- Name: student_academic_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.student_academic_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.student_academic_history_id_seq OWNER TO postgres;

--
-- Name: student_academic_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.student_academic_history_id_seq OWNED BY public.student_academic_history.id;


--
-- Name: student_documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.student_documents (
    id integer NOT NULL,
    student_id integer NOT NULL,
    document_type character varying(50) NOT NULL,
    file_path character varying(255) NOT NULL,
    uploaded_at timestamp without time zone DEFAULT now() NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.student_documents OWNER TO postgres;

--
-- Name: student_documents_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.student_documents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.student_documents_id_seq OWNER TO postgres;

--
-- Name: student_documents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.student_documents_id_seq OWNED BY public.student_documents.id;


--
-- Name: student_fees; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.student_fees (
    id integer NOT NULL,
    student_id integer NOT NULL,
    academic_year_id integer NOT NULL,
    previous_debt numeric(10,2) NOT NULL,
    current_year_fees numeric(10,2) NOT NULL,
    discount_amount numeric(10,2) NOT NULL,
    net_total_required numeric(10,2) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.student_fees OWNER TO postgres;

--
-- Name: student_fees_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.student_fees_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.student_fees_id_seq OWNER TO postgres;

--
-- Name: student_fees_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.student_fees_id_seq OWNED BY public.student_fees.id;


--
-- Name: students; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.students (
    id integer NOT NULL,
    student_number character varying(30) NOT NULL,
    full_name character varying(150) NOT NULL,
    mother_name character varying(150),
    gender character varying(10),
    nationality character varying(50) NOT NULL,
    status character varying(20) NOT NULL,
    enrollment_type character varying(20) NOT NULL,
    student_status_reason character varying(100),
    birth_date date,
    birth_village character varying(50),
    birth_district character varying(50),
    birth_governorate character varying(50),
    transferred_from_school character varying(100),
    transferred_district character varying(50),
    transferred_governorate character varying(50),
    transfer_date date,
    academic_year_id integer,
    grade_id integer,
    section_id integer,
    parent_id integer,
    photo_url character varying(255),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    CONSTRAINT ck_students_enrollment_type CHECK (((enrollment_type)::text = ANY ((ARRAY['مستجد'::character varying, 'محول'::character varying, 'باقي'::character varying])::text[]))),
    CONSTRAINT ck_students_gender CHECK (((gender)::text = ANY ((ARRAY['ذكر'::character varying, 'أنثى'::character varying])::text[]))),
    CONSTRAINT ck_students_status CHECK (((status)::text = ANY ((ARRAY['مستمر'::character varying, 'انسحاب'::character varying, 'موقف'::character varying, 'خريج'::character varying])::text[])))
);


ALTER TABLE public.students OWNER TO postgres;

--
-- Name: students_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.students_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.students_id_seq OWNER TO postgres;

--
-- Name: students_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.students_id_seq OWNED BY public.students.id;


--
-- Name: subjects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subjects (
    id integer NOT NULL,
    subject_name character varying(100) NOT NULL,
    min_pass_score numeric(5,2) NOT NULL,
    max_score numeric(5,2) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.subjects OWNER TO postgres;

--
-- Name: subjects_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.subjects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subjects_id_seq OWNER TO postgres;

--
-- Name: subjects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.subjects_id_seq OWNED BY public.subjects.id;


--
-- Name: system_audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_audit_logs (
    id integer NOT NULL,
    user_id integer,
    module_name character varying(50) NOT NULL,
    operation_type character varying(50) NOT NULL,
    record_id integer,
    old_values text,
    new_values text,
    ip_address character varying(50),
    device_name character varying(100),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.system_audit_logs OWNER TO postgres;

--
-- Name: system_audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.system_audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.system_audit_logs_id_seq OWNER TO postgres;

--
-- Name: system_audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.system_audit_logs_id_seq OWNED BY public.system_audit_logs.id;


--
-- Name: teacher_subject_sections; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teacher_subject_sections (
    id integer NOT NULL,
    academic_year_id integer NOT NULL,
    grade_id integer NOT NULL,
    section_id integer NOT NULL,
    subject_id integer NOT NULL,
    teacher_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.teacher_subject_sections OWNER TO postgres;

--
-- Name: teacher_subject_sections_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.teacher_subject_sections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.teacher_subject_sections_id_seq OWNER TO postgres;

--
-- Name: teacher_subject_sections_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.teacher_subject_sections_id_seq OWNED BY public.teacher_subject_sections.id;


--
-- Name: term_exam_scores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.term_exam_scores (
    id integer NOT NULL,
    student_id integer NOT NULL,
    academic_year_id integer NOT NULL,
    grade_id integer NOT NULL,
    section_id integer NOT NULL,
    subject_id integer NOT NULL,
    term integer NOT NULL,
    exam_score numeric(5,2) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    CONSTRAINT ck_exam_score_max CHECK ((exam_score <= 30.00)),
    CONSTRAINT ck_term_exam_term CHECK ((term = ANY (ARRAY[1, 2])))
);


ALTER TABLE public.term_exam_scores OWNER TO postgres;

--
-- Name: term_exam_scores_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.term_exam_scores_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.term_exam_scores_id_seq OWNER TO postgres;

--
-- Name: term_exam_scores_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.term_exam_scores_id_seq OWNED BY public.term_exam_scores.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    employee_id integer,
    username character varying(50) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role_id integer NOT NULL,
    profile_image character varying(255),
    phone character varying(20),
    email character varying(100),
    status character varying(20) NOT NULL,
    last_login timestamp without time zone,
    last_password_change timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    CONSTRAINT ck_users_status CHECK (((status)::text = ANY ((ARRAY['نشط'::character varying, 'موقف'::character varying])::text[])))
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: weekly_schedules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.weekly_schedules (
    id integer NOT NULL,
    academic_year_id integer NOT NULL,
    term integer NOT NULL,
    grade_id integer NOT NULL,
    section_id integer NOT NULL,
    day_of_week character varying(20) NOT NULL,
    period_number integer NOT NULL,
    subject_id integer,
    teacher_id integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    CONSTRAINT ck_schedule_term CHECK ((term = ANY (ARRAY[1, 2])))
);


ALTER TABLE public.weekly_schedules OWNER TO postgres;

--
-- Name: weekly_schedules_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.weekly_schedules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.weekly_schedules_id_seq OWNER TO postgres;

--
-- Name: weekly_schedules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.weekly_schedules_id_seq OWNED BY public.weekly_schedules.id;


--
-- Name: academic_years id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.academic_years ALTER COLUMN id SET DEFAULT nextval('public.academic_years_id_seq'::regclass);


--
-- Name: annual_closing_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annual_closing_logs ALTER COLUMN id SET DEFAULT nextval('public.annual_closing_logs_id_seq'::regclass);


--
-- Name: backup_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.backup_logs ALTER COLUMN id SET DEFAULT nextval('public.backup_logs_id_seq'::regclass);


--
-- Name: behavioral_records id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.behavioral_records ALTER COLUMN id SET DEFAULT nextval('public.behavioral_records_id_seq'::regclass);


--
-- Name: daily_attendance id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_attendance ALTER COLUMN id SET DEFAULT nextval('public.daily_attendance_id_seq'::regclass);


--
-- Name: employee_allowances_deductions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_allowances_deductions ALTER COLUMN id SET DEFAULT nextval('public.employee_allowances_deductions_id_seq'::regclass);


--
-- Name: employee_loans id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_loans ALTER COLUMN id SET DEFAULT nextval('public.employee_loans_id_seq'::regclass);


--
-- Name: employees id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees ALTER COLUMN id SET DEFAULT nextval('public.employees_id_seq'::regclass);


--
-- Name: expense_vouchers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_vouchers ALTER COLUMN id SET DEFAULT nextval('public.expense_vouchers_id_seq'::regclass);


--
-- Name: fee_installments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fee_installments ALTER COLUMN id SET DEFAULT nextval('public.fee_installments_id_seq'::regclass);


--
-- Name: fee_types id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fee_types ALTER COLUMN id SET DEFAULT nextval('public.fee_types_id_seq'::regclass);


--
-- Name: final_exam_schedules id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.final_exam_schedules ALTER COLUMN id SET DEFAULT nextval('public.final_exam_schedules_id_seq'::regclass);


--
-- Name: grade_fee_structures id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grade_fee_structures ALTER COLUMN id SET DEFAULT nextval('public.grade_fee_structures_id_seq'::regclass);


--
-- Name: grades id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grades ALTER COLUMN id SET DEFAULT nextval('public.grades_id_seq'::regclass);


--
-- Name: homeworks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.homeworks ALTER COLUMN id SET DEFAULT nextval('public.homeworks_id_seq'::regclass);


--
-- Name: import_export_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.import_export_logs ALTER COLUMN id SET DEFAULT nextval('public.import_export_logs_id_seq'::regclass);


--
-- Name: monthly_evaluations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monthly_evaluations ALTER COLUMN id SET DEFAULT nextval('public.monthly_evaluations_id_seq'::regclass);


--
-- Name: monthly_exam_schedules id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monthly_exam_schedules ALTER COLUMN id SET DEFAULT nextval('public.monthly_exam_schedules_id_seq'::regclass);


--
-- Name: notification_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_logs ALTER COLUMN id SET DEFAULT nextval('public.notification_logs_id_seq'::regclass);


--
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- Name: parent_devices id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parent_devices ALTER COLUMN id SET DEFAULT nextval('public.parent_devices_id_seq'::regclass);


--
-- Name: parents id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parents ALTER COLUMN id SET DEFAULT nextval('public.parents_id_seq'::regclass);


--
-- Name: payroll_records id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payroll_records ALTER COLUMN id SET DEFAULT nextval('public.payroll_records_id_seq'::regclass);


--
-- Name: permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions ALTER COLUMN id SET DEFAULT nextval('public.permissions_id_seq'::regclass);


--
-- Name: print_archive id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.print_archive ALTER COLUMN id SET DEFAULT nextval('public.print_archive_id_seq'::regclass);


--
-- Name: receipts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.receipts ALTER COLUMN id SET DEFAULT nextval('public.receipts_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: school_info id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.school_info ALTER COLUMN id SET DEFAULT nextval('public.school_info_id_seq'::regclass);


--
-- Name: sections id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sections ALTER COLUMN id SET DEFAULT nextval('public.sections_id_seq'::regclass);


--
-- Name: student_academic_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_academic_history ALTER COLUMN id SET DEFAULT nextval('public.student_academic_history_id_seq'::regclass);


--
-- Name: student_documents id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_documents ALTER COLUMN id SET DEFAULT nextval('public.student_documents_id_seq'::regclass);


--
-- Name: student_fees id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_fees ALTER COLUMN id SET DEFAULT nextval('public.student_fees_id_seq'::regclass);


--
-- Name: students id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students ALTER COLUMN id SET DEFAULT nextval('public.students_id_seq'::regclass);


--
-- Name: subjects id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subjects ALTER COLUMN id SET DEFAULT nextval('public.subjects_id_seq'::regclass);


--
-- Name: system_audit_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_audit_logs ALTER COLUMN id SET DEFAULT nextval('public.system_audit_logs_id_seq'::regclass);


--
-- Name: teacher_subject_sections id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_subject_sections ALTER COLUMN id SET DEFAULT nextval('public.teacher_subject_sections_id_seq'::regclass);


--
-- Name: term_exam_scores id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.term_exam_scores ALTER COLUMN id SET DEFAULT nextval('public.term_exam_scores_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: weekly_schedules id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weekly_schedules ALTER COLUMN id SET DEFAULT nextval('public.weekly_schedules_id_seq'::regclass);


--
-- Data for Name: academic_years; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.academic_years (id, year_name_gregorian, year_name_hijri, start_date, end_date, is_current, status, is_closed, closed_at, closed_by_user_id, created_at, updated_at) FROM stdin;
2	2	2	2027-08-24	2028-06-24	f	upcoming	f	\N	\N	2026-08-24 03:28:17.45606	2026-08-30 16:42:20.581629
1	2026-2027	1448هـ	2026-01-01	2027-06-30	t	current	f	\N	\N	2026-08-21 02:18:55.676965	2026-08-30 16:47:20.908991
\.


--
-- Data for Name: annual_closing_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.annual_closing_logs (id, from_academic_year_id, to_academic_year_id, total_students_promoted, total_debts_carried_over, executed_by_user_id, execution_date, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: backup_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.backup_logs (id, file_name, file_size, created_at, created_by_user_id, updated_at) FROM stdin;
\.


--
-- Data for Name: behavioral_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.behavioral_records (id, student_id, academic_year_id, behavior_type, title, details, action_taken, record_date, created_at, updated_at) FROM stdin;
1	1	1	تنبيه أخصائي	جلسة إرشادية	تم تسجيل الملاحظة من قبل المعلم	\N	2026-08-23	2026-08-24 22:59:44.680752	\N
2	1	1	تميز	مساعدة زملاء	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-07-12	2026-08-24 22:59:44.680752	\N
3	2	1	مخالفة	تأخر متكرر	تم تسجيل الملاحظة من قبل المعلم	\N	2026-07-02	2026-08-24 22:59:44.680752	\N
4	2	1	تنبيه أخصائي	جلسة إرشادية	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-07-10	2026-08-24 22:59:44.680752	\N
5	3	1	تنبيه أخصائي	جلسة إرشادية	تم تسجيل الملاحظة من قبل المعلم	\N	2026-08-23	2026-08-24 22:59:44.680752	\N
6	3	1	تميز	مشاركة فعالة	تم تسجيل الملاحظة من قبل المعلم	\N	2026-06-30	2026-08-24 22:59:44.680752	\N
7	3	1	تميز	مساعدة زملاء	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-07-13	2026-08-24 22:59:44.680752	\N
8	4	1	تميز	مساعدة زملاء	تم تسجيل الملاحظة من قبل المعلم	\N	2026-07-24	2026-08-24 22:59:44.680752	\N
10	5	1	تنبيه أخصائي	جلسة إرشادية	تم تسجيل الملاحظة من قبل المعلم	\N	2026-08-16	2026-08-24 22:59:44.680752	\N
11	5	1	تنبيه أخصائي	جلسة إرشادية	تم تسجيل الملاحظة من قبل المعلم	\N	2026-07-03	2026-08-24 22:59:44.680752	\N
12	6	1	تنبيه أخصائي	متابعة سلوكية	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-06-27	2026-08-24 22:59:44.680752	\N
13	6	1	تميز	مشاركة فعالة	تم تسجيل الملاحظة من قبل المعلم	\N	2026-08-19	2026-08-24 22:59:44.680752	\N
14	7	1	مخالفة	إزعاج في الفصل	تم تسجيل الملاحظة من قبل المعلم	\N	2026-07-09	2026-08-24 22:59:44.680752	\N
15	7	1	تميز	تفوق دراسي	تم تسجيل الملاحظة من قبل المعلم	\N	2026-07-23	2026-08-24 22:59:44.680752	\N
16	7	1	مخالفة	إزعاج في الفصل	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-08-17	2026-08-24 22:59:44.680752	\N
17	8	1	تميز	تفوق دراسي	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-08-16	2026-08-24 22:59:44.680752	\N
18	9	1	تنبيه أخصائي	متابعة سلوكية	تم تسجيل الملاحظة من قبل المعلم	\N	2026-07-20	2026-08-24 22:59:44.680752	\N
19	9	1	تميز	مساعدة زملاء	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-07-10	2026-08-24 22:59:44.680752	\N
20	9	1	تميز	مساعدة زملاء	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-08-02	2026-08-24 22:59:44.680752	\N
22	10	1	مخالفة	إزعاج في الفصل	تم تسجيل الملاحظة من قبل المعلم	\N	2026-07-14	2026-08-24 22:59:44.680752	\N
23	11	1	مخالفة	إزعاج في الفصل	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-08-07	2026-08-24 22:59:44.680752	\N
24	11	1	تنبيه أخصائي	متابعة سلوكية	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-06-28	2026-08-24 22:59:44.680752	\N
25	11	1	مخالفة	إزعاج في الفصل	تم تسجيل الملاحظة من قبل المعلم	\N	2026-07-17	2026-08-24 22:59:44.680752	\N
26	12	1	تنبيه أخصائي	متابعة سلوكية	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-07-06	2026-08-24 22:59:44.680752	\N
27	13	1	تميز	مشاركة فعالة	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-07-05	2026-08-24 22:59:44.680752	\N
28	13	1	تنبيه أخصائي	متابعة سلوكية	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-07-20	2026-08-24 22:59:44.680752	\N
29	13	1	تميز	مشاركة فعالة	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-06-25	2026-08-24 22:59:44.680752	\N
30	14	1	تميز	تفوق دراسي	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-07-23	2026-08-24 22:59:44.680752	\N
31	14	1	تميز	تفوق دراسي	تم تسجيل الملاحظة من قبل المعلم	\N	2026-07-30	2026-08-24 22:59:44.680752	\N
32	15	1	تميز	مساعدة زملاء	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-07-25	2026-08-24 22:59:44.680752	\N
33	15	1	تنبيه أخصائي	متابعة سلوكية	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-07-29	2026-08-24 22:59:44.680752	\N
34	16	1	تميز	مشاركة فعالة	تم تسجيل الملاحظة من قبل المعلم	\N	2026-07-06	2026-08-24 22:59:44.680752	\N
35	17	1	تميز	تفوق دراسي	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-08-15	2026-08-24 22:59:44.680752	\N
36	18	1	تنبيه أخصائي	جلسة إرشادية	تم تسجيل الملاحظة من قبل المعلم	\N	2026-08-05	2026-08-24 22:59:44.680752	\N
37	19	1	مخالفة	تأخر متكرر	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-08-15	2026-08-24 22:59:44.680752	\N
38	20	1	مخالفة	عدم الالتزام بالزي	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-07-16	2026-08-24 22:59:44.680752	\N
39	21	1	تنبيه أخصائي	متابعة سلوكية	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-07-01	2026-08-24 22:59:44.680752	\N
40	22	1	تنبيه أخصائي	جلسة إرشادية	تم تسجيل الملاحظة من قبل المعلم	\N	2026-07-03	2026-08-24 22:59:44.680752	\N
41	23	1	تميز	تفوق دراسي	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-06-29	2026-08-24 22:59:44.680752	\N
42	23	1	تنبيه أخصائي	متابعة سلوكية	تم تسجيل الملاحظة من قبل المعلم	\N	2026-07-30	2026-08-24 22:59:44.680752	\N
43	23	1	تميز	مشاركة فعالة	تم تسجيل الملاحظة من قبل المعلم	\N	2026-07-31	2026-08-24 22:59:44.680752	\N
44	24	1	تميز	تفوق دراسي	تم تسجيل الملاحظة من قبل المعلم	\N	2026-07-19	2026-08-24 22:59:44.680752	\N
45	25	1	مخالفة	إزعاج في الفصل	تم تسجيل الملاحظة من قبل المعلم	\N	2026-08-02	2026-08-24 22:59:44.680752	\N
46	25	1	تميز	مساعدة زملاء	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-07-13	2026-08-24 22:59:44.680752	\N
47	26	1	تنبيه أخصائي	متابعة سلوكية	تم تسجيل الملاحظة من قبل المعلم	\N	2026-08-13	2026-08-24 22:59:44.680752	\N
48	27	1	تنبيه أخصائي	متابعة سلوكية	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-07-04	2026-08-24 22:59:44.680752	\N
49	27	1	تنبيه أخصائي	جلسة إرشادية	تم تسجيل الملاحظة من قبل المعلم	\N	2026-07-05	2026-08-24 22:59:44.680752	\N
50	28	1	تميز	مشاركة فعالة	تم تسجيل الملاحظة من قبل المعلم	\N	2026-07-18	2026-08-24 22:59:44.680752	\N
51	29	1	تميز	مساعدة زملاء	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-08-23	2026-08-24 22:59:44.680752	\N
52	29	1	تميز	مساعدة زملاء	تم تسجيل الملاحظة من قبل المعلم	\N	2026-07-19	2026-08-24 22:59:44.680752	\N
53	29	1	تميز	مشاركة فعالة	تم تسجيل الملاحظة من قبل المعلم	\N	2026-07-20	2026-08-24 22:59:44.680752	\N
54	30	1	تميز	مساعدة زملاء	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-07-09	2026-08-24 22:59:44.680752	\N
55	30	1	تميز	مساعدة زملاء	تم تسجيل الملاحظة من قبل المعلم	تم إبلاغ ولي الأمر	2026-07-16	2026-08-24 22:59:44.680752	\N
\.


--
-- Data for Name: daily_attendance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.daily_attendance (id, student_id, academic_year_id, grade_id, section_id, attendance_date, status, notes, created_at, updated_at) FROM stdin;
1	1	1	1	1	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
2	1	1	1	1	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
3	1	1	1	1	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
4	1	1	1	1	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
5	1	1	1	1	2026-08-20	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
6	1	1	1	1	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
7	1	1	1	1	2026-08-18	غائب	\N	2026-08-24 22:59:44.680752	\N
8	1	1	1	1	2026-08-17	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
9	1	1	1	1	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
10	1	1	1	1	2026-08-15	غائب	\N	2026-08-24 22:59:44.680752	\N
11	1	1	1	1	2026-08-14	متأخر	\N	2026-08-24 22:59:44.680752	\N
12	1	1	1	1	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
13	1	1	1	1	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
14	1	1	1	1	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
15	1	1	1	1	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
16	1	1	1	1	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
17	1	1	1	1	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
18	1	1	1	1	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
19	1	1	1	1	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
20	1	1	1	1	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
21	1	1	1	1	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
22	1	1	1	1	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
23	1	1	1	1	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
24	1	1	1	1	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
25	1	1	1	1	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
26	1	1	1	1	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
27	1	1	1	1	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
28	1	1	1	1	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
29	1	1	1	1	2026-07-27	متأخر	\N	2026-08-24 22:59:44.680752	\N
30	1	1	1	1	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
31	2	1	1	1	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
32	2	1	1	1	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
33	2	1	1	1	2026-08-22	غائب	\N	2026-08-24 22:59:44.680752	\N
34	2	1	1	1	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
35	2	1	1	1	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
36	2	1	1	1	2026-08-19	غائب	\N	2026-08-24 22:59:44.680752	\N
37	2	1	1	1	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
38	2	1	1	1	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
39	2	1	1	1	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
40	2	1	1	1	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
41	2	1	1	1	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
42	2	1	1	1	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
43	2	1	1	1	2026-08-12	متأخر	\N	2026-08-24 22:59:44.680752	\N
44	2	1	1	1	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
45	2	1	1	1	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
46	2	1	1	1	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
47	2	1	1	1	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
48	2	1	1	1	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
49	2	1	1	1	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
50	2	1	1	1	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
51	2	1	1	1	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
52	2	1	1	1	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
53	2	1	1	1	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
54	2	1	1	1	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
55	2	1	1	1	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
56	2	1	1	1	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
57	2	1	1	1	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
58	2	1	1	1	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
59	2	1	1	1	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
60	2	1	1	1	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
61	3	1	1	1	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
62	3	1	1	1	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
63	3	1	1	1	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
64	3	1	1	1	2026-08-21	متأخر	\N	2026-08-24 22:59:44.680752	\N
65	3	1	1	1	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
66	3	1	1	1	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
67	3	1	1	1	2026-08-18	غائب	\N	2026-08-24 22:59:44.680752	\N
68	3	1	1	1	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
69	3	1	1	1	2026-08-16	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
70	3	1	1	1	2026-08-15	متأخر	\N	2026-08-24 22:59:44.680752	\N
71	3	1	1	1	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
72	3	1	1	1	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
73	3	1	1	1	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
74	3	1	1	1	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
75	3	1	1	1	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
76	3	1	1	1	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
77	3	1	1	1	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
78	3	1	1	1	2026-08-07	غائب	\N	2026-08-24 22:59:44.680752	\N
79	3	1	1	1	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
80	3	1	1	1	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
81	3	1	1	1	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
82	3	1	1	1	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
83	3	1	1	1	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
84	3	1	1	1	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
85	3	1	1	1	2026-07-31	غائب	\N	2026-08-24 22:59:44.680752	\N
86	3	1	1	1	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
87	3	1	1	1	2026-07-29	غائب	\N	2026-08-24 22:59:44.680752	\N
88	3	1	1	1	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
89	3	1	1	1	2026-07-27	غائب	\N	2026-08-24 22:59:44.680752	\N
90	3	1	1	1	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
91	4	1	1	1	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
92	4	1	1	1	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
93	4	1	1	1	2026-08-22	غائب	\N	2026-08-24 22:59:44.680752	\N
94	4	1	1	1	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
95	4	1	1	1	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
96	4	1	1	1	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
97	4	1	1	1	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
98	4	1	1	1	2026-08-17	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
99	4	1	1	1	2026-08-16	متأخر	\N	2026-08-24 22:59:44.680752	\N
100	4	1	1	1	2026-08-15	متأخر	\N	2026-08-24 22:59:44.680752	\N
101	4	1	1	1	2026-08-14	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
102	4	1	1	1	2026-08-13	متأخر	\N	2026-08-24 22:59:44.680752	\N
103	4	1	1	1	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
104	4	1	1	1	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
105	4	1	1	1	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
106	4	1	1	1	2026-08-09	غائب	\N	2026-08-24 22:59:44.680752	\N
107	4	1	1	1	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
108	4	1	1	1	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
109	4	1	1	1	2026-08-06	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
110	4	1	1	1	2026-08-05	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
111	4	1	1	1	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
112	4	1	1	1	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
113	4	1	1	1	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
114	4	1	1	1	2026-08-01	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
115	4	1	1	1	2026-07-31	متأخر	\N	2026-08-24 22:59:44.680752	\N
116	4	1	1	1	2026-07-30	غائب	\N	2026-08-24 22:59:44.680752	\N
117	4	1	1	1	2026-07-29	غائب	\N	2026-08-24 22:59:44.680752	\N
118	4	1	1	1	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
119	4	1	1	1	2026-07-27	غائب	\N	2026-08-24 22:59:44.680752	\N
120	4	1	1	1	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
121	5	1	1	1	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
122	5	1	1	1	2026-08-23	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
123	5	1	1	1	2026-08-22	غائب	\N	2026-08-24 22:59:44.680752	\N
124	5	1	1	1	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
125	5	1	1	1	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
126	5	1	1	1	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
127	5	1	1	1	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
128	5	1	1	1	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
129	5	1	1	1	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
130	5	1	1	1	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
131	5	1	1	1	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
132	5	1	1	1	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
133	5	1	1	1	2026-08-12	متأخر	\N	2026-08-24 22:59:44.680752	\N
134	5	1	1	1	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
135	5	1	1	1	2026-08-10	غائب	\N	2026-08-24 22:59:44.680752	\N
136	5	1	1	1	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
137	5	1	1	1	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
138	5	1	1	1	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
139	5	1	1	1	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
140	5	1	1	1	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
141	5	1	1	1	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
142	5	1	1	1	2026-08-03	متأخر	\N	2026-08-24 22:59:44.680752	\N
143	5	1	1	1	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
144	5	1	1	1	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
145	5	1	1	1	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
146	5	1	1	1	2026-07-30	متأخر	\N	2026-08-24 22:59:44.680752	\N
147	5	1	1	1	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
148	5	1	1	1	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
149	5	1	1	1	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
150	5	1	1	1	2026-07-26	متأخر	\N	2026-08-24 22:59:44.680752	\N
151	6	1	1	1	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
152	6	1	1	1	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
153	6	1	1	1	2026-08-22	متأخر	\N	2026-08-24 22:59:44.680752	\N
154	6	1	1	1	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
155	6	1	1	1	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
156	6	1	1	1	2026-08-19	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
157	6	1	1	1	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
158	6	1	1	1	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
159	6	1	1	1	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
160	6	1	1	1	2026-08-15	غائب	\N	2026-08-24 22:59:44.680752	\N
161	6	1	1	1	2026-08-14	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
162	6	1	1	1	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
163	6	1	1	1	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
164	6	1	1	1	2026-08-11	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
165	6	1	1	1	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
166	6	1	1	1	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
167	6	1	1	1	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
168	6	1	1	1	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
169	6	1	1	1	2026-08-06	غائب	\N	2026-08-24 22:59:44.680752	\N
170	6	1	1	1	2026-08-05	متأخر	\N	2026-08-24 22:59:44.680752	\N
171	6	1	1	1	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
172	6	1	1	1	2026-08-03	غائب	\N	2026-08-24 22:59:44.680752	\N
173	6	1	1	1	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
174	6	1	1	1	2026-08-01	غائب	\N	2026-08-24 22:59:44.680752	\N
175	6	1	1	1	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
176	6	1	1	1	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
177	6	1	1	1	2026-07-29	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
178	6	1	1	1	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
179	6	1	1	1	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
180	6	1	1	1	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
181	7	1	1	1	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
182	7	1	1	1	2026-08-23	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
183	7	1	1	1	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
184	7	1	1	1	2026-08-21	متأخر	\N	2026-08-24 22:59:44.680752	\N
185	7	1	1	1	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
186	7	1	1	1	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
187	7	1	1	1	2026-08-18	متأخر	\N	2026-08-24 22:59:44.680752	\N
188	7	1	1	1	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
189	7	1	1	1	2026-08-16	غائب	\N	2026-08-24 22:59:44.680752	\N
190	7	1	1	1	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
191	7	1	1	1	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
192	7	1	1	1	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
193	7	1	1	1	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
194	7	1	1	1	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
195	7	1	1	1	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
196	7	1	1	1	2026-08-09	غائب	\N	2026-08-24 22:59:44.680752	\N
197	7	1	1	1	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
198	7	1	1	1	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
199	7	1	1	1	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
200	7	1	1	1	2026-08-05	متأخر	\N	2026-08-24 22:59:44.680752	\N
201	7	1	1	1	2026-08-04	غائب	\N	2026-08-24 22:59:44.680752	\N
202	7	1	1	1	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
203	7	1	1	1	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
204	7	1	1	1	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
205	7	1	1	1	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
206	7	1	1	1	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
207	7	1	1	1	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
208	7	1	1	1	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
209	7	1	1	1	2026-07-27	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
210	7	1	1	1	2026-07-26	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
211	8	1	1	1	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
212	8	1	1	1	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
213	8	1	1	1	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
214	8	1	1	1	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
215	8	1	1	1	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
216	8	1	1	1	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
217	8	1	1	1	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
218	8	1	1	1	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
219	8	1	1	1	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
220	8	1	1	1	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
221	8	1	1	1	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
222	8	1	1	1	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
223	8	1	1	1	2026-08-12	متأخر	\N	2026-08-24 22:59:44.680752	\N
224	8	1	1	1	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
225	8	1	1	1	2026-08-10	غائب	\N	2026-08-24 22:59:44.680752	\N
226	8	1	1	1	2026-08-09	متأخر	\N	2026-08-24 22:59:44.680752	\N
227	8	1	1	1	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
228	8	1	1	1	2026-08-07	غائب	\N	2026-08-24 22:59:44.680752	\N
229	8	1	1	1	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
230	8	1	1	1	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
231	8	1	1	1	2026-08-04	غائب	\N	2026-08-24 22:59:44.680752	\N
232	8	1	1	1	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
233	8	1	1	1	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
234	8	1	1	1	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
235	8	1	1	1	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
236	8	1	1	1	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
237	8	1	1	1	2026-07-29	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
238	8	1	1	1	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
239	8	1	1	1	2026-07-27	غائب	\N	2026-08-24 22:59:44.680752	\N
240	8	1	1	1	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
241	9	1	1	1	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
242	9	1	1	1	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
243	9	1	1	1	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
244	9	1	1	1	2026-08-21	غائب	\N	2026-08-24 22:59:44.680752	\N
245	9	1	1	1	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
246	9	1	1	1	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
247	9	1	1	1	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
248	9	1	1	1	2026-08-17	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
249	9	1	1	1	2026-08-16	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
250	9	1	1	1	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
251	9	1	1	1	2026-08-14	غائب	\N	2026-08-24 22:59:44.680752	\N
252	9	1	1	1	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
253	9	1	1	1	2026-08-12	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
254	9	1	1	1	2026-08-11	متأخر	\N	2026-08-24 22:59:44.680752	\N
255	9	1	1	1	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
256	9	1	1	1	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
257	9	1	1	1	2026-08-08	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
258	9	1	1	1	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
259	9	1	1	1	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
260	9	1	1	1	2026-08-05	متأخر	\N	2026-08-24 22:59:44.680752	\N
261	9	1	1	1	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
262	9	1	1	1	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
263	9	1	1	1	2026-08-02	غائب	\N	2026-08-24 22:59:44.680752	\N
264	9	1	1	1	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
265	9	1	1	1	2026-07-31	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
266	9	1	1	1	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
267	9	1	1	1	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
268	9	1	1	1	2026-07-28	غائب	\N	2026-08-24 22:59:44.680752	\N
269	9	1	1	1	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
270	9	1	1	1	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
271	10	1	1	1	2026-08-24	غائب	\N	2026-08-24 22:59:44.680752	\N
272	10	1	1	1	2026-08-23	غائب	\N	2026-08-24 22:59:44.680752	\N
273	10	1	1	1	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
274	10	1	1	1	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
275	10	1	1	1	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
276	10	1	1	1	2026-08-19	غائب	\N	2026-08-24 22:59:44.680752	\N
277	10	1	1	1	2026-08-18	متأخر	\N	2026-08-24 22:59:44.680752	\N
278	10	1	1	1	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
279	10	1	1	1	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
280	10	1	1	1	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
281	10	1	1	1	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
282	10	1	1	1	2026-08-13	متأخر	\N	2026-08-24 22:59:44.680752	\N
283	10	1	1	1	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
284	10	1	1	1	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
285	10	1	1	1	2026-08-10	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
286	10	1	1	1	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
287	10	1	1	1	2026-08-08	غائب	\N	2026-08-24 22:59:44.680752	\N
288	10	1	1	1	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
289	10	1	1	1	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
290	10	1	1	1	2026-08-05	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
291	10	1	1	1	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
292	10	1	1	1	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
293	10	1	1	1	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
294	10	1	1	1	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
295	10	1	1	1	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
296	10	1	1	1	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
297	10	1	1	1	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
298	10	1	1	1	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
299	10	1	1	1	2026-07-27	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
300	10	1	1	1	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
301	11	1	1	1	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
302	11	1	1	1	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
303	11	1	1	1	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
304	11	1	1	1	2026-08-21	غائب	\N	2026-08-24 22:59:44.680752	\N
305	11	1	1	1	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
306	11	1	1	1	2026-08-19	غائب	\N	2026-08-24 22:59:44.680752	\N
307	11	1	1	1	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
308	11	1	1	1	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
309	11	1	1	1	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
310	11	1	1	1	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
311	11	1	1	1	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
312	11	1	1	1	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
313	11	1	1	1	2026-08-12	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
314	11	1	1	1	2026-08-11	غائب	\N	2026-08-24 22:59:44.680752	\N
315	11	1	1	1	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
316	11	1	1	1	2026-08-09	غائب	\N	2026-08-24 22:59:44.680752	\N
317	11	1	1	1	2026-08-08	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
318	11	1	1	1	2026-08-07	متأخر	\N	2026-08-24 22:59:44.680752	\N
319	11	1	1	1	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
320	11	1	1	1	2026-08-05	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
321	11	1	1	1	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
322	11	1	1	1	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
323	11	1	1	1	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
324	11	1	1	1	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
325	11	1	1	1	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
326	11	1	1	1	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
327	11	1	1	1	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
328	11	1	1	1	2026-07-28	متأخر	\N	2026-08-24 22:59:44.680752	\N
329	11	1	1	1	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
330	11	1	1	1	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
331	12	1	1	1	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
332	12	1	1	1	2026-08-23	غائب	\N	2026-08-24 22:59:44.680752	\N
333	12	1	1	1	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
334	12	1	1	1	2026-08-21	متأخر	\N	2026-08-24 22:59:44.680752	\N
335	12	1	1	1	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
336	12	1	1	1	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
337	12	1	1	1	2026-08-18	غائب	\N	2026-08-24 22:59:44.680752	\N
338	12	1	1	1	2026-08-17	غائب	\N	2026-08-24 22:59:44.680752	\N
339	12	1	1	1	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
340	12	1	1	1	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
341	12	1	1	1	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
342	12	1	1	1	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
343	12	1	1	1	2026-08-12	غائب	\N	2026-08-24 22:59:44.680752	\N
344	12	1	1	1	2026-08-11	متأخر	\N	2026-08-24 22:59:44.680752	\N
345	12	1	1	1	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
346	12	1	1	1	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
347	12	1	1	1	2026-08-08	غائب	\N	2026-08-24 22:59:44.680752	\N
348	12	1	1	1	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
349	12	1	1	1	2026-08-06	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
350	12	1	1	1	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
351	12	1	1	1	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
352	12	1	1	1	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
353	12	1	1	1	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
354	12	1	1	1	2026-08-01	متأخر	\N	2026-08-24 22:59:44.680752	\N
355	12	1	1	1	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
356	12	1	1	1	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
357	12	1	1	1	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
358	12	1	1	1	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
359	12	1	1	1	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
360	12	1	1	1	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
361	13	1	1	1	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
362	13	1	1	1	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
363	13	1	1	1	2026-08-22	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
364	13	1	1	1	2026-08-21	متأخر	\N	2026-08-24 22:59:44.680752	\N
365	13	1	1	1	2026-08-20	غائب	\N	2026-08-24 22:59:44.680752	\N
366	13	1	1	1	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
367	13	1	1	1	2026-08-18	غائب	\N	2026-08-24 22:59:44.680752	\N
368	13	1	1	1	2026-08-17	غائب	\N	2026-08-24 22:59:44.680752	\N
369	13	1	1	1	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
370	13	1	1	1	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
371	13	1	1	1	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
372	13	1	1	1	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
373	13	1	1	1	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
374	13	1	1	1	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
375	13	1	1	1	2026-08-10	غائب	\N	2026-08-24 22:59:44.680752	\N
376	13	1	1	1	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
377	13	1	1	1	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
378	13	1	1	1	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
379	13	1	1	1	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
380	13	1	1	1	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
381	13	1	1	1	2026-08-04	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
382	13	1	1	1	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
383	13	1	1	1	2026-08-02	غائب	\N	2026-08-24 22:59:44.680752	\N
384	13	1	1	1	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
385	13	1	1	1	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
386	13	1	1	1	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
387	13	1	1	1	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
388	13	1	1	1	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
389	13	1	1	1	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
390	13	1	1	1	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
391	14	1	1	1	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
392	14	1	1	1	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
393	14	1	1	1	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
394	14	1	1	1	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
395	14	1	1	1	2026-08-20	غائب	\N	2026-08-24 22:59:44.680752	\N
396	14	1	1	1	2026-08-19	متأخر	\N	2026-08-24 22:59:44.680752	\N
397	14	1	1	1	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
398	14	1	1	1	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
399	14	1	1	1	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
400	14	1	1	1	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
401	14	1	1	1	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
402	14	1	1	1	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
403	14	1	1	1	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
404	14	1	1	1	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
405	14	1	1	1	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
406	14	1	1	1	2026-08-09	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
407	14	1	1	1	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
408	14	1	1	1	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
409	14	1	1	1	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
410	14	1	1	1	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
411	14	1	1	1	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
412	14	1	1	1	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
413	14	1	1	1	2026-08-02	غائب	\N	2026-08-24 22:59:44.680752	\N
414	14	1	1	1	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
415	14	1	1	1	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
416	14	1	1	1	2026-07-30	غائب	\N	2026-08-24 22:59:44.680752	\N
417	14	1	1	1	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
418	14	1	1	1	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
419	14	1	1	1	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
420	14	1	1	1	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
421	15	1	1	1	2026-08-24	متأخر	\N	2026-08-24 22:59:44.680752	\N
422	15	1	1	1	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
423	15	1	1	1	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
424	15	1	1	1	2026-08-21	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
425	15	1	1	1	2026-08-20	غائب	\N	2026-08-24 22:59:44.680752	\N
426	15	1	1	1	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
427	15	1	1	1	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
428	15	1	1	1	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
429	15	1	1	1	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
430	15	1	1	1	2026-08-15	متأخر	\N	2026-08-24 22:59:44.680752	\N
431	15	1	1	1	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
432	15	1	1	1	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
433	15	1	1	1	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
434	15	1	1	1	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
435	15	1	1	1	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
436	15	1	1	1	2026-08-09	متأخر	\N	2026-08-24 22:59:44.680752	\N
437	15	1	1	1	2026-08-08	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
438	15	1	1	1	2026-08-07	متأخر	\N	2026-08-24 22:59:44.680752	\N
439	15	1	1	1	2026-08-06	غائب	\N	2026-08-24 22:59:44.680752	\N
440	15	1	1	1	2026-08-05	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
441	15	1	1	1	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
442	15	1	1	1	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
443	15	1	1	1	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
444	15	1	1	1	2026-08-01	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
445	15	1	1	1	2026-07-31	غائب	\N	2026-08-24 22:59:44.680752	\N
446	15	1	1	1	2026-07-30	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
447	15	1	1	1	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
448	15	1	1	1	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
449	15	1	1	1	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
450	15	1	1	1	2026-07-26	غائب	\N	2026-08-24 22:59:44.680752	\N
451	16	1	1	1	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
452	16	1	1	1	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
453	16	1	1	1	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
454	16	1	1	1	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
455	16	1	1	1	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
456	16	1	1	1	2026-08-19	غائب	\N	2026-08-24 22:59:44.680752	\N
457	16	1	1	1	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
458	16	1	1	1	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
459	16	1	1	1	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
460	16	1	1	1	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
461	16	1	1	1	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
462	16	1	1	1	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
463	16	1	1	1	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
464	16	1	1	1	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
465	16	1	1	1	2026-08-10	غائب	\N	2026-08-24 22:59:44.680752	\N
466	16	1	1	1	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
467	16	1	1	1	2026-08-08	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
468	16	1	1	1	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
469	16	1	1	1	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
470	16	1	1	1	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
471	16	1	1	1	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
472	16	1	1	1	2026-08-03	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
473	16	1	1	1	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
474	16	1	1	1	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
475	16	1	1	1	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
476	16	1	1	1	2026-07-30	غائب	\N	2026-08-24 22:59:44.680752	\N
477	16	1	1	1	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
478	16	1	1	1	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
479	16	1	1	1	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
480	16	1	1	1	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
481	17	1	1	1	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
482	17	1	1	1	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
483	17	1	1	1	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
484	17	1	1	1	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
485	17	1	1	1	2026-08-20	غائب	\N	2026-08-24 22:59:44.680752	\N
486	17	1	1	1	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
487	17	1	1	1	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
488	17	1	1	1	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
489	17	1	1	1	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
490	17	1	1	1	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
491	17	1	1	1	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
492	17	1	1	1	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
493	17	1	1	1	2026-08-12	متأخر	\N	2026-08-24 22:59:44.680752	\N
494	17	1	1	1	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
495	17	1	1	1	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
496	17	1	1	1	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
497	17	1	1	1	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
498	17	1	1	1	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
499	17	1	1	1	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
500	17	1	1	1	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
501	17	1	1	1	2026-08-04	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
502	17	1	1	1	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
503	17	1	1	1	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
504	17	1	1	1	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
505	17	1	1	1	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
506	17	1	1	1	2026-07-30	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
507	17	1	1	1	2026-07-29	غائب	\N	2026-08-24 22:59:44.680752	\N
508	17	1	1	1	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
509	17	1	1	1	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
510	17	1	1	1	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
511	18	1	1	1	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
512	18	1	1	1	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
513	18	1	1	1	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
514	18	1	1	1	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
515	18	1	1	1	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
516	18	1	1	1	2026-08-19	غائب	\N	2026-08-24 22:59:44.680752	\N
517	18	1	1	1	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
518	18	1	1	1	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
519	18	1	1	1	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
520	18	1	1	1	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
521	18	1	1	1	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
522	18	1	1	1	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
523	18	1	1	1	2026-08-12	غائب	\N	2026-08-24 22:59:44.680752	\N
524	18	1	1	1	2026-08-11	غائب	\N	2026-08-24 22:59:44.680752	\N
525	18	1	1	1	2026-08-10	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
526	18	1	1	1	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
527	18	1	1	1	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
528	18	1	1	1	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
529	18	1	1	1	2026-08-06	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
530	18	1	1	1	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
531	18	1	1	1	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
532	18	1	1	1	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
533	18	1	1	1	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
534	18	1	1	1	2026-08-01	متأخر	\N	2026-08-24 22:59:44.680752	\N
535	18	1	1	1	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
536	18	1	1	1	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
537	18	1	1	1	2026-07-29	غائب	\N	2026-08-24 22:59:44.680752	\N
538	18	1	1	1	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
539	18	1	1	1	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
540	18	1	1	1	2026-07-26	غائب	\N	2026-08-24 22:59:44.680752	\N
541	19	1	1	1	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
542	19	1	1	1	2026-08-23	متأخر	\N	2026-08-24 22:59:44.680752	\N
543	19	1	1	1	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
544	19	1	1	1	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
545	19	1	1	1	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
546	19	1	1	1	2026-08-19	متأخر	\N	2026-08-24 22:59:44.680752	\N
547	19	1	1	1	2026-08-18	متأخر	\N	2026-08-24 22:59:44.680752	\N
548	19	1	1	1	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
549	19	1	1	1	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
550	19	1	1	1	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
551	19	1	1	1	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
552	19	1	1	1	2026-08-13	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
553	19	1	1	1	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
554	19	1	1	1	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
555	19	1	1	1	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
556	19	1	1	1	2026-08-09	غائب	\N	2026-08-24 22:59:44.680752	\N
557	19	1	1	1	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
558	19	1	1	1	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
559	19	1	1	1	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
560	19	1	1	1	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
561	19	1	1	1	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
562	19	1	1	1	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
563	19	1	1	1	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
564	19	1	1	1	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
565	19	1	1	1	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
566	19	1	1	1	2026-07-30	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
567	19	1	1	1	2026-07-29	غائب	\N	2026-08-24 22:59:44.680752	\N
568	19	1	1	1	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
569	19	1	1	1	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
570	19	1	1	1	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
571	20	1	1	2	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
572	20	1	1	2	2026-08-23	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
573	20	1	1	2	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
574	20	1	1	2	2026-08-21	غائب	\N	2026-08-24 22:59:44.680752	\N
575	20	1	1	2	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
576	20	1	1	2	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
577	20	1	1	2	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
578	20	1	1	2	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
579	20	1	1	2	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
580	20	1	1	2	2026-08-15	متأخر	\N	2026-08-24 22:59:44.680752	\N
581	20	1	1	2	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
582	20	1	1	2	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
583	20	1	1	2	2026-08-12	متأخر	\N	2026-08-24 22:59:44.680752	\N
584	20	1	1	2	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
585	20	1	1	2	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
586	20	1	1	2	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
587	20	1	1	2	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
588	20	1	1	2	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
589	20	1	1	2	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
590	20	1	1	2	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
591	20	1	1	2	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
592	20	1	1	2	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
593	20	1	1	2	2026-08-02	غائب	\N	2026-08-24 22:59:44.680752	\N
594	20	1	1	2	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
595	20	1	1	2	2026-07-31	غائب	\N	2026-08-24 22:59:44.680752	\N
596	20	1	1	2	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
597	20	1	1	2	2026-07-29	غائب	\N	2026-08-24 22:59:44.680752	\N
598	20	1	1	2	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
599	20	1	1	2	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
600	20	1	1	2	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
601	21	1	1	2	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
602	21	1	1	2	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
603	21	1	1	2	2026-08-22	غائب	\N	2026-08-24 22:59:44.680752	\N
604	21	1	1	2	2026-08-21	غائب	\N	2026-08-24 22:59:44.680752	\N
605	21	1	1	2	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
606	21	1	1	2	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
607	21	1	1	2	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
608	21	1	1	2	2026-08-17	غائب	\N	2026-08-24 22:59:44.680752	\N
609	21	1	1	2	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
610	21	1	1	2	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
611	21	1	1	2	2026-08-14	غائب	\N	2026-08-24 22:59:44.680752	\N
612	21	1	1	2	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
613	21	1	1	2	2026-08-12	متأخر	\N	2026-08-24 22:59:44.680752	\N
614	21	1	1	2	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
615	21	1	1	2	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
616	21	1	1	2	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
617	21	1	1	2	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
618	21	1	1	2	2026-08-07	غائب	\N	2026-08-24 22:59:44.680752	\N
619	21	1	1	2	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
620	21	1	1	2	2026-08-05	غائب	\N	2026-08-24 22:59:44.680752	\N
621	21	1	1	2	2026-08-04	غائب	\N	2026-08-24 22:59:44.680752	\N
622	21	1	1	2	2026-08-03	غائب	\N	2026-08-24 22:59:44.680752	\N
623	21	1	1	2	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
624	21	1	1	2	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
625	21	1	1	2	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
626	21	1	1	2	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
627	21	1	1	2	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
628	21	1	1	2	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
629	21	1	1	2	2026-07-27	غائب	\N	2026-08-24 22:59:44.680752	\N
630	21	1	1	2	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
631	22	1	1	2	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
632	22	1	1	2	2026-08-23	غائب	\N	2026-08-24 22:59:44.680752	\N
633	22	1	1	2	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
634	22	1	1	2	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
635	22	1	1	2	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
636	22	1	1	2	2026-08-19	متأخر	\N	2026-08-24 22:59:44.680752	\N
637	22	1	1	2	2026-08-18	غائب	\N	2026-08-24 22:59:44.680752	\N
638	22	1	1	2	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
639	22	1	1	2	2026-08-16	متأخر	\N	2026-08-24 22:59:44.680752	\N
640	22	1	1	2	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
641	22	1	1	2	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
642	22	1	1	2	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
643	22	1	1	2	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
644	22	1	1	2	2026-08-11	متأخر	\N	2026-08-24 22:59:44.680752	\N
645	22	1	1	2	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
646	22	1	1	2	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
647	22	1	1	2	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
648	22	1	1	2	2026-08-07	متأخر	\N	2026-08-24 22:59:44.680752	\N
649	22	1	1	2	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
650	22	1	1	2	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
651	22	1	1	2	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
652	22	1	1	2	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
653	22	1	1	2	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
654	22	1	1	2	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
655	22	1	1	2	2026-07-31	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
656	22	1	1	2	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
657	22	1	1	2	2026-07-29	غائب	\N	2026-08-24 22:59:44.680752	\N
658	22	1	1	2	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
659	22	1	1	2	2026-07-27	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
660	22	1	1	2	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
661	23	1	1	2	2026-08-24	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
662	23	1	1	2	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
663	23	1	1	2	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
664	23	1	1	2	2026-08-21	غائب	\N	2026-08-24 22:59:44.680752	\N
665	23	1	1	2	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
666	23	1	1	2	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
667	23	1	1	2	2026-08-18	غائب	\N	2026-08-24 22:59:44.680752	\N
668	23	1	1	2	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
669	23	1	1	2	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
670	23	1	1	2	2026-08-15	غائب	\N	2026-08-24 22:59:44.680752	\N
671	23	1	1	2	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
672	23	1	1	2	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
673	23	1	1	2	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
674	23	1	1	2	2026-08-11	غائب	\N	2026-08-24 22:59:44.680752	\N
675	23	1	1	2	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
676	23	1	1	2	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
677	23	1	1	2	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
678	23	1	1	2	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
679	23	1	1	2	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
680	23	1	1	2	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
681	23	1	1	2	2026-08-04	غائب	\N	2026-08-24 22:59:44.680752	\N
682	23	1	1	2	2026-08-03	غائب	\N	2026-08-24 22:59:44.680752	\N
683	23	1	1	2	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
684	23	1	1	2	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
685	23	1	1	2	2026-07-31	متأخر	\N	2026-08-24 22:59:44.680752	\N
686	23	1	1	2	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
687	23	1	1	2	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
688	23	1	1	2	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
689	23	1	1	2	2026-07-27	غائب	\N	2026-08-24 22:59:44.680752	\N
690	23	1	1	2	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
691	24	1	1	2	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
692	24	1	1	2	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
693	24	1	1	2	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
694	24	1	1	2	2026-08-21	غائب	\N	2026-08-24 22:59:44.680752	\N
695	24	1	1	2	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
696	24	1	1	2	2026-08-19	غائب	\N	2026-08-24 22:59:44.680752	\N
697	24	1	1	2	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
698	24	1	1	2	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
699	24	1	1	2	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
700	24	1	1	2	2026-08-15	متأخر	\N	2026-08-24 22:59:44.680752	\N
701	24	1	1	2	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
702	24	1	1	2	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
703	24	1	1	2	2026-08-12	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
704	24	1	1	2	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
705	24	1	1	2	2026-08-10	غائب	\N	2026-08-24 22:59:44.680752	\N
706	24	1	1	2	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
707	24	1	1	2	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
708	24	1	1	2	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
709	24	1	1	2	2026-08-06	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
710	24	1	1	2	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
711	24	1	1	2	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
712	24	1	1	2	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
713	24	1	1	2	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
714	24	1	1	2	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
715	24	1	1	2	2026-07-31	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
716	24	1	1	2	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
717	24	1	1	2	2026-07-29	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
718	24	1	1	2	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
719	24	1	1	2	2026-07-27	غائب	\N	2026-08-24 22:59:44.680752	\N
720	24	1	1	2	2026-07-26	متأخر	\N	2026-08-24 22:59:44.680752	\N
721	25	1	1	2	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
722	25	1	1	2	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
723	25	1	1	2	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
724	25	1	1	2	2026-08-21	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
725	25	1	1	2	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
726	25	1	1	2	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
727	25	1	1	2	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
728	25	1	1	2	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
729	25	1	1	2	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
730	25	1	1	2	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
731	25	1	1	2	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
732	25	1	1	2	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
733	25	1	1	2	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
734	25	1	1	2	2026-08-11	غائب	\N	2026-08-24 22:59:44.680752	\N
735	25	1	1	2	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
736	25	1	1	2	2026-08-09	غائب	\N	2026-08-24 22:59:44.680752	\N
737	25	1	1	2	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
738	25	1	1	2	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
739	25	1	1	2	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
740	25	1	1	2	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
741	25	1	1	2	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
742	25	1	1	2	2026-08-03	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
743	25	1	1	2	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
744	25	1	1	2	2026-08-01	متأخر	\N	2026-08-24 22:59:44.680752	\N
745	25	1	1	2	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
746	25	1	1	2	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
747	25	1	1	2	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
748	25	1	1	2	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
749	25	1	1	2	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
750	25	1	1	2	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
751	26	1	1	2	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
752	26	1	1	2	2026-08-23	متأخر	\N	2026-08-24 22:59:44.680752	\N
753	26	1	1	2	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
754	26	1	1	2	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
755	26	1	1	2	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
756	26	1	1	2	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
757	26	1	1	2	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
758	26	1	1	2	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
759	26	1	1	2	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
760	26	1	1	2	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
761	26	1	1	2	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
762	26	1	1	2	2026-08-13	غائب	\N	2026-08-24 22:59:44.680752	\N
763	26	1	1	2	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
764	26	1	1	2	2026-08-11	متأخر	\N	2026-08-24 22:59:44.680752	\N
765	26	1	1	2	2026-08-10	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
766	26	1	1	2	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
767	26	1	1	2	2026-08-08	غائب	\N	2026-08-24 22:59:44.680752	\N
768	26	1	1	2	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
769	26	1	1	2	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
770	26	1	1	2	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
771	26	1	1	2	2026-08-04	غائب	\N	2026-08-24 22:59:44.680752	\N
772	26	1	1	2	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
773	26	1	1	2	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
774	26	1	1	2	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
775	26	1	1	2	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
776	26	1	1	2	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
777	26	1	1	2	2026-07-29	متأخر	\N	2026-08-24 22:59:44.680752	\N
778	26	1	1	2	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
779	26	1	1	2	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
780	26	1	1	2	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
781	27	1	1	2	2026-08-24	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
782	27	1	1	2	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
783	27	1	1	2	2026-08-22	غائب	\N	2026-08-24 22:59:44.680752	\N
784	27	1	1	2	2026-08-21	غائب	\N	2026-08-24 22:59:44.680752	\N
785	27	1	1	2	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
786	27	1	1	2	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
787	27	1	1	2	2026-08-18	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
788	27	1	1	2	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
789	27	1	1	2	2026-08-16	متأخر	\N	2026-08-24 22:59:44.680752	\N
790	27	1	1	2	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
791	27	1	1	2	2026-08-14	غائب	\N	2026-08-24 22:59:44.680752	\N
792	27	1	1	2	2026-08-13	غائب	\N	2026-08-24 22:59:44.680752	\N
793	27	1	1	2	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
794	27	1	1	2	2026-08-11	غائب	\N	2026-08-24 22:59:44.680752	\N
795	27	1	1	2	2026-08-10	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
796	27	1	1	2	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
797	27	1	1	2	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
798	27	1	1	2	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
799	27	1	1	2	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
800	27	1	1	2	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
801	27	1	1	2	2026-08-04	متأخر	\N	2026-08-24 22:59:44.680752	\N
802	27	1	1	2	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
803	27	1	1	2	2026-08-02	غائب	\N	2026-08-24 22:59:44.680752	\N
804	27	1	1	2	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
805	27	1	1	2	2026-07-31	غائب	\N	2026-08-24 22:59:44.680752	\N
806	27	1	1	2	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
807	27	1	1	2	2026-07-29	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
808	27	1	1	2	2026-07-28	غائب	\N	2026-08-24 22:59:44.680752	\N
809	27	1	1	2	2026-07-27	غائب	\N	2026-08-24 22:59:44.680752	\N
810	27	1	1	2	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
811	28	1	1	2	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
812	28	1	1	2	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
813	28	1	1	2	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
814	28	1	1	2	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
815	28	1	1	2	2026-08-20	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
816	28	1	1	2	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
817	28	1	1	2	2026-08-18	متأخر	\N	2026-08-24 22:59:44.680752	\N
818	28	1	1	2	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
819	28	1	1	2	2026-08-16	غائب	\N	2026-08-24 22:59:44.680752	\N
820	28	1	1	2	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
821	28	1	1	2	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
822	28	1	1	2	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
823	28	1	1	2	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
824	28	1	1	2	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
825	28	1	1	2	2026-08-10	غائب	\N	2026-08-24 22:59:44.680752	\N
826	28	1	1	2	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
827	28	1	1	2	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
828	28	1	1	2	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
829	28	1	1	2	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
830	28	1	1	2	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
831	28	1	1	2	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
832	28	1	1	2	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
833	28	1	1	2	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
834	28	1	1	2	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
835	28	1	1	2	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
836	28	1	1	2	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
837	28	1	1	2	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
838	28	1	1	2	2026-07-28	غائب	\N	2026-08-24 22:59:44.680752	\N
839	28	1	1	2	2026-07-27	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
840	28	1	1	2	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
841	29	1	1	2	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
842	29	1	1	2	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
843	29	1	1	2	2026-08-22	غائب	\N	2026-08-24 22:59:44.680752	\N
844	29	1	1	2	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
845	29	1	1	2	2026-08-20	متأخر	\N	2026-08-24 22:59:44.680752	\N
846	29	1	1	2	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
847	29	1	1	2	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
848	29	1	1	2	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
849	29	1	1	2	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
850	29	1	1	2	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
851	29	1	1	2	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
852	29	1	1	2	2026-08-13	غائب	\N	2026-08-24 22:59:44.680752	\N
853	29	1	1	2	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
854	29	1	1	2	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
855	29	1	1	2	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
856	29	1	1	2	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
857	29	1	1	2	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
858	29	1	1	2	2026-08-07	متأخر	\N	2026-08-24 22:59:44.680752	\N
859	29	1	1	2	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
860	29	1	1	2	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
861	29	1	1	2	2026-08-04	متأخر	\N	2026-08-24 22:59:44.680752	\N
862	29	1	1	2	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
863	29	1	1	2	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
864	29	1	1	2	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
865	29	1	1	2	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
866	29	1	1	2	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
867	29	1	1	2	2026-07-29	متأخر	\N	2026-08-24 22:59:44.680752	\N
868	29	1	1	2	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
869	29	1	1	2	2026-07-27	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
870	29	1	1	2	2026-07-26	غائب	\N	2026-08-24 22:59:44.680752	\N
871	30	1	1	2	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
872	30	1	1	2	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
873	30	1	1	2	2026-08-22	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
874	30	1	1	2	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
875	30	1	1	2	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
876	30	1	1	2	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
877	30	1	1	2	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
878	30	1	1	2	2026-08-17	غائب	\N	2026-08-24 22:59:44.680752	\N
879	30	1	1	2	2026-08-16	متأخر	\N	2026-08-24 22:59:44.680752	\N
880	30	1	1	2	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
881	30	1	1	2	2026-08-14	غائب	\N	2026-08-24 22:59:44.680752	\N
882	30	1	1	2	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
883	30	1	1	2	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
884	30	1	1	2	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
885	30	1	1	2	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
886	30	1	1	2	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
887	30	1	1	2	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
888	30	1	1	2	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
889	30	1	1	2	2026-08-06	متأخر	\N	2026-08-24 22:59:44.680752	\N
890	30	1	1	2	2026-08-05	غائب	\N	2026-08-24 22:59:44.680752	\N
891	30	1	1	2	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
892	30	1	1	2	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
893	30	1	1	2	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
894	30	1	1	2	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
895	30	1	1	2	2026-07-31	غائب	\N	2026-08-24 22:59:44.680752	\N
896	30	1	1	2	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
897	30	1	1	2	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
898	30	1	1	2	2026-07-28	غائب	\N	2026-08-24 22:59:44.680752	\N
899	30	1	1	2	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
900	30	1	1	2	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
901	31	1	1	2	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
902	31	1	1	2	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
903	31	1	1	2	2026-08-22	متأخر	\N	2026-08-24 22:59:44.680752	\N
904	31	1	1	2	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
905	31	1	1	2	2026-08-20	متأخر	\N	2026-08-24 22:59:44.680752	\N
906	31	1	1	2	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
907	31	1	1	2	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
908	31	1	1	2	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
909	31	1	1	2	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
910	31	1	1	2	2026-08-15	غائب	\N	2026-08-24 22:59:44.680752	\N
911	31	1	1	2	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
912	31	1	1	2	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
913	31	1	1	2	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
914	31	1	1	2	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
915	31	1	1	2	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
916	31	1	1	2	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
917	31	1	1	2	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
918	31	1	1	2	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
919	31	1	1	2	2026-08-06	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
920	31	1	1	2	2026-08-05	غائب	\N	2026-08-24 22:59:44.680752	\N
921	31	1	1	2	2026-08-04	غائب	\N	2026-08-24 22:59:44.680752	\N
922	31	1	1	2	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
923	31	1	1	2	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
924	31	1	1	2	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
925	31	1	1	2	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
926	31	1	1	2	2026-07-30	متأخر	\N	2026-08-24 22:59:44.680752	\N
927	31	1	1	2	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
928	31	1	1	2	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
929	31	1	1	2	2026-07-27	متأخر	\N	2026-08-24 22:59:44.680752	\N
930	31	1	1	2	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
931	32	1	1	2	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
932	32	1	1	2	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
933	32	1	1	2	2026-08-22	غائب	\N	2026-08-24 22:59:44.680752	\N
934	32	1	1	2	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
935	32	1	1	2	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
936	32	1	1	2	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
937	32	1	1	2	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
938	32	1	1	2	2026-08-17	غائب	\N	2026-08-24 22:59:44.680752	\N
939	32	1	1	2	2026-08-16	متأخر	\N	2026-08-24 22:59:44.680752	\N
940	32	1	1	2	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
941	32	1	1	2	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
942	32	1	1	2	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
943	32	1	1	2	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
944	32	1	1	2	2026-08-11	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
945	32	1	1	2	2026-08-10	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
946	32	1	1	2	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
947	32	1	1	2	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
948	32	1	1	2	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
949	32	1	1	2	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
950	32	1	1	2	2026-08-05	غائب	\N	2026-08-24 22:59:44.680752	\N
951	32	1	1	2	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
952	32	1	1	2	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
953	32	1	1	2	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
954	32	1	1	2	2026-08-01	متأخر	\N	2026-08-24 22:59:44.680752	\N
955	32	1	1	2	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
956	32	1	1	2	2026-07-30	غائب	\N	2026-08-24 22:59:44.680752	\N
957	32	1	1	2	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
958	32	1	1	2	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
959	32	1	1	2	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
960	32	1	1	2	2026-07-26	غائب	\N	2026-08-24 22:59:44.680752	\N
961	33	1	1	2	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
962	33	1	1	2	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
963	33	1	1	2	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
964	33	1	1	2	2026-08-21	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
965	33	1	1	2	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
966	33	1	1	2	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
967	33	1	1	2	2026-08-18	غائب	\N	2026-08-24 22:59:44.680752	\N
968	33	1	1	2	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
969	33	1	1	2	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
970	33	1	1	2	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
971	33	1	1	2	2026-08-14	غائب	\N	2026-08-24 22:59:44.680752	\N
972	33	1	1	2	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
973	33	1	1	2	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
974	33	1	1	2	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
975	33	1	1	2	2026-08-10	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
976	33	1	1	2	2026-08-09	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
977	33	1	1	2	2026-08-08	متأخر	\N	2026-08-24 22:59:44.680752	\N
978	33	1	1	2	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
979	33	1	1	2	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
980	33	1	1	2	2026-08-05	متأخر	\N	2026-08-24 22:59:44.680752	\N
981	33	1	1	2	2026-08-04	متأخر	\N	2026-08-24 22:59:44.680752	\N
982	33	1	1	2	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
983	33	1	1	2	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
984	33	1	1	2	2026-08-01	غائب	\N	2026-08-24 22:59:44.680752	\N
985	33	1	1	2	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
986	33	1	1	2	2026-07-30	غائب	\N	2026-08-24 22:59:44.680752	\N
987	33	1	1	2	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
988	33	1	1	2	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
989	33	1	1	2	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
990	33	1	1	2	2026-07-26	غائب	\N	2026-08-24 22:59:44.680752	\N
991	34	1	1	2	2026-08-24	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
992	34	1	1	2	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
993	34	1	1	2	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
994	34	1	1	2	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
995	34	1	1	2	2026-08-20	متأخر	\N	2026-08-24 22:59:44.680752	\N
996	34	1	1	2	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
997	34	1	1	2	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
998	34	1	1	2	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
999	34	1	1	2	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
1000	34	1	1	2	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
1001	34	1	1	2	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
1002	34	1	1	2	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
1003	34	1	1	2	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
1004	34	1	1	2	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
1005	34	1	1	2	2026-08-10	غائب	\N	2026-08-24 22:59:44.680752	\N
1006	34	1	1	2	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
1007	34	1	1	2	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
1008	34	1	1	2	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
1009	34	1	1	2	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
1010	34	1	1	2	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
1011	34	1	1	2	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
1012	34	1	1	2	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
1013	34	1	1	2	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
1014	34	1	1	2	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
1015	34	1	1	2	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
1016	34	1	1	2	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
1017	34	1	1	2	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
1018	34	1	1	2	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
1019	34	1	1	2	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
1020	34	1	1	2	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
1021	35	1	1	3	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
1022	35	1	1	3	2026-08-23	غائب	\N	2026-08-24 22:59:44.680752	\N
1023	35	1	1	3	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
1024	35	1	1	3	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
1025	35	1	1	3	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
1026	35	1	1	3	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
1027	35	1	1	3	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
1028	35	1	1	3	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
1029	35	1	1	3	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
1030	35	1	1	3	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
1031	35	1	1	3	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
1032	35	1	1	3	2026-08-13	غائب	\N	2026-08-24 22:59:44.680752	\N
1033	35	1	1	3	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
1034	35	1	1	3	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
1035	35	1	1	3	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
1036	35	1	1	3	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
1037	35	1	1	3	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
1038	35	1	1	3	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
1039	35	1	1	3	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
1040	35	1	1	3	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
1041	35	1	1	3	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
1042	35	1	1	3	2026-08-03	غائب	\N	2026-08-24 22:59:44.680752	\N
1043	35	1	1	3	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
1044	35	1	1	3	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
1045	35	1	1	3	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
1046	35	1	1	3	2026-07-30	غائب	\N	2026-08-24 22:59:44.680752	\N
1047	35	1	1	3	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
1048	35	1	1	3	2026-07-28	غائب	\N	2026-08-24 22:59:44.680752	\N
1049	35	1	1	3	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
1050	35	1	1	3	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
1051	36	1	1	3	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
1052	36	1	1	3	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
1053	36	1	1	3	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
1054	36	1	1	3	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
1055	36	1	1	3	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
1056	36	1	1	3	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
1057	36	1	1	3	2026-08-18	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1058	36	1	1	3	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
1059	36	1	1	3	2026-08-16	غائب	\N	2026-08-24 22:59:44.680752	\N
1060	36	1	1	3	2026-08-15	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1061	36	1	1	3	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
1062	36	1	1	3	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
1063	36	1	1	3	2026-08-12	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1064	36	1	1	3	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
1065	36	1	1	3	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
1066	36	1	1	3	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
1067	36	1	1	3	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
1068	36	1	1	3	2026-08-07	متأخر	\N	2026-08-24 22:59:44.680752	\N
1069	36	1	1	3	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
1070	36	1	1	3	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
1071	36	1	1	3	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
1072	36	1	1	3	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
1073	36	1	1	3	2026-08-02	متأخر	\N	2026-08-24 22:59:44.680752	\N
1074	36	1	1	3	2026-08-01	غائب	\N	2026-08-24 22:59:44.680752	\N
1075	36	1	1	3	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
1076	36	1	1	3	2026-07-30	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1077	36	1	1	3	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
1078	36	1	1	3	2026-07-28	متأخر	\N	2026-08-24 22:59:44.680752	\N
1079	36	1	1	3	2026-07-27	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1080	36	1	1	3	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
1081	37	1	1	3	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
1082	37	1	1	3	2026-08-23	متأخر	\N	2026-08-24 22:59:44.680752	\N
1083	37	1	1	3	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
1084	37	1	1	3	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
1085	37	1	1	3	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
1086	37	1	1	3	2026-08-19	غائب	\N	2026-08-24 22:59:44.680752	\N
1087	37	1	1	3	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
1088	37	1	1	3	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
1089	37	1	1	3	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
1090	37	1	1	3	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
1091	37	1	1	3	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
1092	37	1	1	3	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
1093	37	1	1	3	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
1094	37	1	1	3	2026-08-11	متأخر	\N	2026-08-24 22:59:44.680752	\N
1095	37	1	1	3	2026-08-10	غائب	\N	2026-08-24 22:59:44.680752	\N
1096	37	1	1	3	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
1097	37	1	1	3	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
1098	37	1	1	3	2026-08-07	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1099	37	1	1	3	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
1100	37	1	1	3	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
1101	37	1	1	3	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
1102	37	1	1	3	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
1103	37	1	1	3	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
1104	37	1	1	3	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
1105	37	1	1	3	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
1106	37	1	1	3	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
1107	37	1	1	3	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
1108	37	1	1	3	2026-07-28	متأخر	\N	2026-08-24 22:59:44.680752	\N
1109	37	1	1	3	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
1110	37	1	1	3	2026-07-26	متأخر	\N	2026-08-24 22:59:44.680752	\N
1111	38	1	1	3	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
1112	38	1	1	3	2026-08-23	غائب	\N	2026-08-24 22:59:44.680752	\N
1113	38	1	1	3	2026-08-22	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1114	38	1	1	3	2026-08-21	غائب	\N	2026-08-24 22:59:44.680752	\N
1115	38	1	1	3	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
1116	38	1	1	3	2026-08-19	غائب	\N	2026-08-24 22:59:44.680752	\N
1117	38	1	1	3	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
1118	38	1	1	3	2026-08-17	غائب	\N	2026-08-24 22:59:44.680752	\N
1119	38	1	1	3	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
1120	38	1	1	3	2026-08-15	غائب	\N	2026-08-24 22:59:44.680752	\N
1121	38	1	1	3	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
1122	38	1	1	3	2026-08-13	متأخر	\N	2026-08-24 22:59:44.680752	\N
1123	38	1	1	3	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
1124	38	1	1	3	2026-08-11	متأخر	\N	2026-08-24 22:59:44.680752	\N
1125	38	1	1	3	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
1126	38	1	1	3	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
1127	38	1	1	3	2026-08-08	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1128	38	1	1	3	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
1129	38	1	1	3	2026-08-06	غائب	\N	2026-08-24 22:59:44.680752	\N
1130	38	1	1	3	2026-08-05	متأخر	\N	2026-08-24 22:59:44.680752	\N
1131	38	1	1	3	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
1132	38	1	1	3	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
1133	38	1	1	3	2026-08-02	غائب	\N	2026-08-24 22:59:44.680752	\N
1134	38	1	1	3	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
1135	38	1	1	3	2026-07-31	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1136	38	1	1	3	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
1137	38	1	1	3	2026-07-29	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1138	38	1	1	3	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
1139	38	1	1	3	2026-07-27	متأخر	\N	2026-08-24 22:59:44.680752	\N
1140	38	1	1	3	2026-07-26	غائب	\N	2026-08-24 22:59:44.680752	\N
1141	39	1	1	3	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
1142	39	1	1	3	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
1143	39	1	1	3	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
1144	39	1	1	3	2026-08-21	غائب	\N	2026-08-24 22:59:44.680752	\N
1145	39	1	1	3	2026-08-20	متأخر	\N	2026-08-24 22:59:44.680752	\N
1146	39	1	1	3	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
1147	39	1	1	3	2026-08-18	غائب	\N	2026-08-24 22:59:44.680752	\N
1148	39	1	1	3	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
1149	39	1	1	3	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
1150	39	1	1	3	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
1151	39	1	1	3	2026-08-14	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1152	39	1	1	3	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
1153	39	1	1	3	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
1154	39	1	1	3	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
1155	39	1	1	3	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
1156	39	1	1	3	2026-08-09	غائب	\N	2026-08-24 22:59:44.680752	\N
1157	39	1	1	3	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
1158	39	1	1	3	2026-08-07	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1159	39	1	1	3	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
1160	39	1	1	3	2026-08-05	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1161	39	1	1	3	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
1162	39	1	1	3	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
1163	39	1	1	3	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
1164	39	1	1	3	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
1165	39	1	1	3	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
1166	39	1	1	3	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
1167	39	1	1	3	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
1168	39	1	1	3	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
1169	39	1	1	3	2026-07-27	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1170	39	1	1	3	2026-07-26	متأخر	\N	2026-08-24 22:59:44.680752	\N
1171	40	1	1	3	2026-08-24	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1172	40	1	1	3	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
1173	40	1	1	3	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
1174	40	1	1	3	2026-08-21	متأخر	\N	2026-08-24 22:59:44.680752	\N
1175	40	1	1	3	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
1176	40	1	1	3	2026-08-19	غائب	\N	2026-08-24 22:59:44.680752	\N
1177	40	1	1	3	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
1178	40	1	1	3	2026-08-17	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1179	40	1	1	3	2026-08-16	متأخر	\N	2026-08-24 22:59:44.680752	\N
1180	40	1	1	3	2026-08-15	غائب	\N	2026-08-24 22:59:44.680752	\N
1181	40	1	1	3	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
1182	40	1	1	3	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
1183	40	1	1	3	2026-08-12	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1184	40	1	1	3	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
1185	40	1	1	3	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
1186	40	1	1	3	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
1187	40	1	1	3	2026-08-08	غائب	\N	2026-08-24 22:59:44.680752	\N
1188	40	1	1	3	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
1189	40	1	1	3	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
1190	40	1	1	3	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
1191	40	1	1	3	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
1192	40	1	1	3	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
1193	40	1	1	3	2026-08-02	غائب	\N	2026-08-24 22:59:44.680752	\N
1194	40	1	1	3	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
1195	40	1	1	3	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
1196	40	1	1	3	2026-07-30	متأخر	\N	2026-08-24 22:59:44.680752	\N
1197	40	1	1	3	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
1198	40	1	1	3	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
1199	40	1	1	3	2026-07-27	غائب	\N	2026-08-24 22:59:44.680752	\N
1200	40	1	1	3	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
1201	41	1	1	3	2026-08-24	غائب	\N	2026-08-24 22:59:44.680752	\N
1202	41	1	1	3	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
1203	41	1	1	3	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
1204	41	1	1	3	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
1205	41	1	1	3	2026-08-20	غائب	\N	2026-08-24 22:59:44.680752	\N
1206	41	1	1	3	2026-08-19	متأخر	\N	2026-08-24 22:59:44.680752	\N
1207	41	1	1	3	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
1208	41	1	1	3	2026-08-17	غائب	\N	2026-08-24 22:59:44.680752	\N
1209	41	1	1	3	2026-08-16	متأخر	\N	2026-08-24 22:59:44.680752	\N
1210	41	1	1	3	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
1211	41	1	1	3	2026-08-14	غائب	\N	2026-08-24 22:59:44.680752	\N
1212	41	1	1	3	2026-08-13	غائب	\N	2026-08-24 22:59:44.680752	\N
1213	41	1	1	3	2026-08-12	غائب	\N	2026-08-24 22:59:44.680752	\N
1214	41	1	1	3	2026-08-11	غائب	\N	2026-08-24 22:59:44.680752	\N
1215	41	1	1	3	2026-08-10	متأخر	\N	2026-08-24 22:59:44.680752	\N
1216	41	1	1	3	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
1217	41	1	1	3	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
1218	41	1	1	3	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
1219	41	1	1	3	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
1220	41	1	1	3	2026-08-05	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1221	41	1	1	3	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
1222	41	1	1	3	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
1223	41	1	1	3	2026-08-02	متأخر	\N	2026-08-24 22:59:44.680752	\N
1224	41	1	1	3	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
1225	41	1	1	3	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
1226	41	1	1	3	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
1227	41	1	1	3	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
1228	41	1	1	3	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
1229	41	1	1	3	2026-07-27	غائب	\N	2026-08-24 22:59:44.680752	\N
1230	41	1	1	3	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
1231	42	1	1	3	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
1232	42	1	1	3	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
1233	42	1	1	3	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
1234	42	1	1	3	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
1235	42	1	1	3	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
1236	42	1	1	3	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
1237	42	1	1	3	2026-08-18	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1238	42	1	1	3	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
1239	42	1	1	3	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
1240	42	1	1	3	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
1241	42	1	1	3	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
1242	42	1	1	3	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
1243	42	1	1	3	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
1244	42	1	1	3	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
1245	42	1	1	3	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
1246	42	1	1	3	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
1247	42	1	1	3	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
1248	42	1	1	3	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
1249	42	1	1	3	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
1250	42	1	1	3	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
1251	42	1	1	3	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
1252	42	1	1	3	2026-08-03	غائب	\N	2026-08-24 22:59:44.680752	\N
1253	42	1	1	3	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
1254	42	1	1	3	2026-08-01	غائب	\N	2026-08-24 22:59:44.680752	\N
1255	42	1	1	3	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
1256	42	1	1	3	2026-07-30	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1257	42	1	1	3	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
1258	42	1	1	3	2026-07-28	متأخر	\N	2026-08-24 22:59:44.680752	\N
1259	42	1	1	3	2026-07-27	متأخر	\N	2026-08-24 22:59:44.680752	\N
1260	42	1	1	3	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
1261	43	1	1	3	2026-08-24	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1262	43	1	1	3	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
1263	43	1	1	3	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
1264	43	1	1	3	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
1265	43	1	1	3	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
1266	43	1	1	3	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
1267	43	1	1	3	2026-08-18	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1268	43	1	1	3	2026-08-17	متأخر	\N	2026-08-24 22:59:44.680752	\N
1269	43	1	1	3	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
1270	43	1	1	3	2026-08-15	غائب	\N	2026-08-24 22:59:44.680752	\N
1271	43	1	1	3	2026-08-14	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1272	43	1	1	3	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
1273	43	1	1	3	2026-08-12	غائب	\N	2026-08-24 22:59:44.680752	\N
1274	43	1	1	3	2026-08-11	متأخر	\N	2026-08-24 22:59:44.680752	\N
1275	43	1	1	3	2026-08-10	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1276	43	1	1	3	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
1277	43	1	1	3	2026-08-08	غائب	\N	2026-08-24 22:59:44.680752	\N
1278	43	1	1	3	2026-08-07	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1279	43	1	1	3	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
1280	43	1	1	3	2026-08-05	غائب	\N	2026-08-24 22:59:44.680752	\N
1281	43	1	1	3	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
1282	43	1	1	3	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
1283	43	1	1	3	2026-08-02	غائب	\N	2026-08-24 22:59:44.680752	\N
1284	43	1	1	3	2026-08-01	متأخر	\N	2026-08-24 22:59:44.680752	\N
1285	43	1	1	3	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
1286	43	1	1	3	2026-07-30	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1287	43	1	1	3	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
1288	43	1	1	3	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
1289	43	1	1	3	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
1290	43	1	1	3	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
1291	44	1	1	3	2026-08-24	متأخر	\N	2026-08-24 22:59:44.680752	\N
1292	44	1	1	3	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
1293	44	1	1	3	2026-08-22	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1294	44	1	1	3	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
1295	44	1	1	3	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
1296	44	1	1	3	2026-08-19	متأخر	\N	2026-08-24 22:59:44.680752	\N
1297	44	1	1	3	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
1298	44	1	1	3	2026-08-17	غائب	\N	2026-08-24 22:59:44.680752	\N
1299	44	1	1	3	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
1300	44	1	1	3	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
1301	44	1	1	3	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
1302	44	1	1	3	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
1303	44	1	1	3	2026-08-12	متأخر	\N	2026-08-24 22:59:44.680752	\N
1304	44	1	1	3	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
1305	44	1	1	3	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
1306	44	1	1	3	2026-08-09	غائب	\N	2026-08-24 22:59:44.680752	\N
1307	44	1	1	3	2026-08-08	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1308	44	1	1	3	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
1309	44	1	1	3	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
1310	44	1	1	3	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
1311	44	1	1	3	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
1312	44	1	1	3	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
1313	44	1	1	3	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
1314	44	1	1	3	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
1315	44	1	1	3	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
1316	44	1	1	3	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
1317	44	1	1	3	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
1318	44	1	1	3	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
1319	44	1	1	3	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
1320	44	1	1	3	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
1321	45	1	1	3	2026-08-24	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1322	45	1	1	3	2026-08-23	غائب	\N	2026-08-24 22:59:44.680752	\N
1323	45	1	1	3	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
1324	45	1	1	3	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
1325	45	1	1	3	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
1326	45	1	1	3	2026-08-19	متأخر	\N	2026-08-24 22:59:44.680752	\N
1327	45	1	1	3	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
1328	45	1	1	3	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
1329	45	1	1	3	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
1330	45	1	1	3	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
1331	45	1	1	3	2026-08-14	غائب	\N	2026-08-24 22:59:44.680752	\N
1332	45	1	1	3	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
1333	45	1	1	3	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
1334	45	1	1	3	2026-08-11	غائب	\N	2026-08-24 22:59:44.680752	\N
1335	45	1	1	3	2026-08-10	غائب	\N	2026-08-24 22:59:44.680752	\N
1336	45	1	1	3	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
1337	45	1	1	3	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
1338	45	1	1	3	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
1339	45	1	1	3	2026-08-06	غائب	\N	2026-08-24 22:59:44.680752	\N
1340	45	1	1	3	2026-08-05	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1341	45	1	1	3	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
1342	45	1	1	3	2026-08-03	متأخر	\N	2026-08-24 22:59:44.680752	\N
1343	45	1	1	3	2026-08-02	غائب	\N	2026-08-24 22:59:44.680752	\N
1344	45	1	1	3	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
1345	45	1	1	3	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
1346	45	1	1	3	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
1347	45	1	1	3	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
1348	45	1	1	3	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
1349	45	1	1	3	2026-07-27	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1350	45	1	1	3	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
1351	46	1	1	3	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
1352	46	1	1	3	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
1353	46	1	1	3	2026-08-22	غائب	\N	2026-08-24 22:59:44.680752	\N
1354	46	1	1	3	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
1355	46	1	1	3	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
1356	46	1	1	3	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
1357	46	1	1	3	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
1358	46	1	1	3	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
1359	46	1	1	3	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
1360	46	1	1	3	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
1361	46	1	1	3	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
1362	46	1	1	3	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
1363	46	1	1	3	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
1364	46	1	1	3	2026-08-11	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1365	46	1	1	3	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
1366	46	1	1	3	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
1367	46	1	1	3	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
1368	46	1	1	3	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
1369	46	1	1	3	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
1370	46	1	1	3	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
1371	46	1	1	3	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
1372	46	1	1	3	2026-08-03	متأخر	\N	2026-08-24 22:59:44.680752	\N
1373	46	1	1	3	2026-08-02	غائب	\N	2026-08-24 22:59:44.680752	\N
1374	46	1	1	3	2026-08-01	غائب	\N	2026-08-24 22:59:44.680752	\N
1375	46	1	1	3	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
1376	46	1	1	3	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
1377	46	1	1	3	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
1378	46	1	1	3	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
1379	46	1	1	3	2026-07-27	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1380	46	1	1	3	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
1381	47	1	1	3	2026-08-24	غائب	\N	2026-08-24 22:59:44.680752	\N
1382	47	1	1	3	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
1383	47	1	1	3	2026-08-22	غائب	\N	2026-08-24 22:59:44.680752	\N
1384	47	1	1	3	2026-08-21	متأخر	\N	2026-08-24 22:59:44.680752	\N
1385	47	1	1	3	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
1386	47	1	1	3	2026-08-19	غائب	\N	2026-08-24 22:59:44.680752	\N
1387	47	1	1	3	2026-08-18	غائب	\N	2026-08-24 22:59:44.680752	\N
1388	47	1	1	3	2026-08-17	متأخر	\N	2026-08-24 22:59:44.680752	\N
1389	47	1	1	3	2026-08-16	غائب	\N	2026-08-24 22:59:44.680752	\N
1390	47	1	1	3	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
1391	47	1	1	3	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
1392	47	1	1	3	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
1393	47	1	1	3	2026-08-12	غائب	\N	2026-08-24 22:59:44.680752	\N
1394	47	1	1	3	2026-08-11	غائب	\N	2026-08-24 22:59:44.680752	\N
1395	47	1	1	3	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
1396	47	1	1	3	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
1397	47	1	1	3	2026-08-08	غائب	\N	2026-08-24 22:59:44.680752	\N
1398	47	1	1	3	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
1399	47	1	1	3	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
1400	47	1	1	3	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
1401	47	1	1	3	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
1402	47	1	1	3	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
1403	47	1	1	3	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
1404	47	1	1	3	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
1405	47	1	1	3	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
1406	47	1	1	3	2026-07-30	غائب	\N	2026-08-24 22:59:44.680752	\N
1407	47	1	1	3	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
1408	47	1	1	3	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
1409	47	1	1	3	2026-07-27	حاضر	\N	2026-08-24 22:59:44.680752	\N
1410	47	1	1	3	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
1411	48	1	1	3	2026-08-24	حاضر	\N	2026-08-24 22:59:44.680752	\N
1412	48	1	1	3	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
1413	48	1	1	3	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
1414	48	1	1	3	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
1415	48	1	1	3	2026-08-20	غائب	\N	2026-08-24 22:59:44.680752	\N
1416	48	1	1	3	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
1417	48	1	1	3	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
1418	48	1	1	3	2026-08-17	حاضر	\N	2026-08-24 22:59:44.680752	\N
1419	48	1	1	3	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
1420	48	1	1	3	2026-08-15	غائب	\N	2026-08-24 22:59:44.680752	\N
1421	48	1	1	3	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
1422	48	1	1	3	2026-08-13	غائب	\N	2026-08-24 22:59:44.680752	\N
1423	48	1	1	3	2026-08-12	متأخر	\N	2026-08-24 22:59:44.680752	\N
1424	48	1	1	3	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
1425	48	1	1	3	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
1426	48	1	1	3	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
1427	48	1	1	3	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
1428	48	1	1	3	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
1429	48	1	1	3	2026-08-06	غائب	\N	2026-08-24 22:59:44.680752	\N
1430	48	1	1	3	2026-08-05	غائب	\N	2026-08-24 22:59:44.680752	\N
1431	48	1	1	3	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
1432	48	1	1	3	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
1433	48	1	1	3	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
1434	48	1	1	3	2026-08-01	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1435	48	1	1	3	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
1436	48	1	1	3	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
1437	48	1	1	3	2026-07-29	غائب	\N	2026-08-24 22:59:44.680752	\N
1438	48	1	1	3	2026-07-28	متأخر	\N	2026-08-24 22:59:44.680752	\N
1439	48	1	1	3	2026-07-27	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1440	48	1	1	3	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
1441	49	1	1	3	2026-08-24	غائب	\N	2026-08-24 22:59:44.680752	\N
1442	49	1	1	3	2026-08-23	حاضر	\N	2026-08-24 22:59:44.680752	\N
1443	49	1	1	3	2026-08-22	متأخر	\N	2026-08-24 22:59:44.680752	\N
1444	49	1	1	3	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
1445	49	1	1	3	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
1446	49	1	1	3	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
1447	49	1	1	3	2026-08-18	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1448	49	1	1	3	2026-08-17	غائب	\N	2026-08-24 22:59:44.680752	\N
1449	49	1	1	3	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
1450	49	1	1	3	2026-08-15	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1451	49	1	1	3	2026-08-14	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1452	49	1	1	3	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
1453	49	1	1	3	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
1454	49	1	1	3	2026-08-11	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1455	49	1	1	3	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
1456	49	1	1	3	2026-08-09	حاضر	\N	2026-08-24 22:59:44.680752	\N
1457	49	1	1	3	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
1458	49	1	1	3	2026-08-07	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1459	49	1	1	3	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
1460	49	1	1	3	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
1461	49	1	1	3	2026-08-04	غائب	\N	2026-08-24 22:59:44.680752	\N
1462	49	1	1	3	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
1463	49	1	1	3	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
1464	49	1	1	3	2026-08-01	حاضر	\N	2026-08-24 22:59:44.680752	\N
1465	49	1	1	3	2026-07-31	غائب	\N	2026-08-24 22:59:44.680752	\N
1466	49	1	1	3	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
1467	49	1	1	3	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
1468	49	1	1	3	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
1469	49	1	1	3	2026-07-27	غائب	\N	2026-08-24 22:59:44.680752	\N
1470	49	1	1	3	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
1471	50	1	1	3	2026-08-24	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1472	50	1	1	3	2026-08-23	متأخر	متأخر عن الطابور	2026-08-24 22:59:44.680752	\N
1473	50	1	1	3	2026-08-22	حاضر	\N	2026-08-24 22:59:44.680752	\N
1474	50	1	1	3	2026-08-21	حاضر	\N	2026-08-24 22:59:44.680752	\N
1475	50	1	1	3	2026-08-20	حاضر	\N	2026-08-24 22:59:44.680752	\N
1476	50	1	1	3	2026-08-19	حاضر	\N	2026-08-24 22:59:44.680752	\N
1477	50	1	1	3	2026-08-18	حاضر	\N	2026-08-24 22:59:44.680752	\N
1478	50	1	1	3	2026-08-17	متأخر	\N	2026-08-24 22:59:44.680752	\N
1479	50	1	1	3	2026-08-16	حاضر	\N	2026-08-24 22:59:44.680752	\N
1480	50	1	1	3	2026-08-15	حاضر	\N	2026-08-24 22:59:44.680752	\N
1481	50	1	1	3	2026-08-14	حاضر	\N	2026-08-24 22:59:44.680752	\N
1482	50	1	1	3	2026-08-13	حاضر	\N	2026-08-24 22:59:44.680752	\N
1483	50	1	1	3	2026-08-12	حاضر	\N	2026-08-24 22:59:44.680752	\N
1484	50	1	1	3	2026-08-11	حاضر	\N	2026-08-24 22:59:44.680752	\N
1485	50	1	1	3	2026-08-10	حاضر	\N	2026-08-24 22:59:44.680752	\N
1486	50	1	1	3	2026-08-09	غائب	\N	2026-08-24 22:59:44.680752	\N
1487	50	1	1	3	2026-08-08	حاضر	\N	2026-08-24 22:59:44.680752	\N
1488	50	1	1	3	2026-08-07	حاضر	\N	2026-08-24 22:59:44.680752	\N
1489	50	1	1	3	2026-08-06	حاضر	\N	2026-08-24 22:59:44.680752	\N
1490	50	1	1	3	2026-08-05	حاضر	\N	2026-08-24 22:59:44.680752	\N
1491	50	1	1	3	2026-08-04	حاضر	\N	2026-08-24 22:59:44.680752	\N
1492	50	1	1	3	2026-08-03	حاضر	\N	2026-08-24 22:59:44.680752	\N
1493	50	1	1	3	2026-08-02	حاضر	\N	2026-08-24 22:59:44.680752	\N
1494	50	1	1	3	2026-08-01	غائب	\N	2026-08-24 22:59:44.680752	\N
1495	50	1	1	3	2026-07-31	حاضر	\N	2026-08-24 22:59:44.680752	\N
1496	50	1	1	3	2026-07-30	حاضر	\N	2026-08-24 22:59:44.680752	\N
1497	50	1	1	3	2026-07-29	حاضر	\N	2026-08-24 22:59:44.680752	\N
1498	50	1	1	3	2026-07-28	حاضر	\N	2026-08-24 22:59:44.680752	\N
1499	50	1	1	3	2026-07-27	متأخر	\N	2026-08-24 22:59:44.680752	\N
1500	50	1	1	3	2026-07-26	حاضر	\N	2026-08-24 22:59:44.680752	\N
1501	693	1	1	1	2026-08-25	غائب		2026-08-25 05:42:45.268489	\N
1502	18	1	1	1	2026-08-25	غائب		2026-08-25 05:42:45.268489	\N
1503	14	1	1	1	2026-08-25	حاضر		2026-08-25 05:42:45.268489	\N
1504	6	1	1	1	2026-08-25	حاضر		2026-08-25 05:42:45.268489	\N
1505	7	1	1	1	2026-08-25	حاضر		2026-08-25 05:42:45.268489	\N
1506	10	1	1	1	2026-08-25	حاضر		2026-08-25 05:42:45.268489	\N
1507	12	1	1	1	2026-08-25	حاضر		2026-08-25 05:42:45.268489	\N
1508	16	1	1	1	2026-08-25	حاضر		2026-08-25 05:42:45.268489	\N
1509	3	1	1	1	2026-08-25	حاضر		2026-08-25 05:42:45.268489	\N
1510	13	1	1	1	2026-08-25	حاضر		2026-08-25 05:42:45.268489	\N
1511	17	1	1	1	2026-08-25	حاضر		2026-08-25 05:42:45.268489	\N
1512	11	1	1	1	2026-08-25	حاضر		2026-08-25 05:42:45.268489	\N
1513	4	1	1	1	2026-08-25	حاضر		2026-08-25 05:42:45.268489	\N
1514	15	1	1	1	2026-08-25	حاضر		2026-08-25 05:42:45.268489	\N
1515	5	1	1	1	2026-08-25	حاضر		2026-08-25 05:42:45.268489	\N
1516	8	1	1	1	2026-08-25	حاضر		2026-08-25 05:42:45.268489	\N
1517	18	1	1	1	2026-08-29	غائب		2026-08-29 03:35:51.673331	\N
1518	14	1	1	1	2026-08-29	غائب بمبرر		2026-08-29 03:35:51.673331	\N
1519	6	1	1	1	2026-08-29	حاضر		2026-08-29 03:35:51.673331	\N
1520	7	1	1	1	2026-08-29	حاضر		2026-08-29 03:35:51.673331	\N
1521	10	1	1	1	2026-08-29	حاضر		2026-08-29 03:35:51.673331	\N
1522	12	1	1	1	2026-08-29	حاضر		2026-08-29 03:35:51.673331	\N
1523	16	1	1	1	2026-08-29	حاضر		2026-08-29 03:35:51.673331	\N
1524	3	1	1	1	2026-08-29	حاضر		2026-08-29 03:35:51.673331	\N
1525	13	1	1	1	2026-08-29	حاضر		2026-08-29 03:35:51.673331	\N
1526	17	1	1	1	2026-08-29	حاضر		2026-08-29 03:35:51.673331	\N
1527	4	1	1	1	2026-08-29	حاضر		2026-08-29 03:35:51.673331	\N
1528	11	1	1	1	2026-08-29	حاضر		2026-08-29 03:35:51.673331	\N
1529	15	1	1	1	2026-08-29	حاضر		2026-08-29 03:35:51.673331	\N
1530	5	1	1	1	2026-08-29	حاضر		2026-08-29 03:35:51.673331	\N
1531	8	1	1	1	2026-08-29	حاضر		2026-08-29 03:35:51.673331	\N
1602	18	1	1	1	2026-08-30	حاضر	ww	2026-08-30 17:40:03.096855	\N
1603	14	1	1	1	2026-08-30	غائب	w	2026-08-30 17:40:03.096855	\N
1604	6	1	1	1	2026-08-30	حاضر		2026-08-30 17:40:03.096855	\N
1605	7	1	1	1	2026-08-30	حاضر		2026-08-30 17:40:03.096855	\N
1606	10	1	1	1	2026-08-30	حاضر		2026-08-30 17:40:03.096855	\N
1607	12	1	1	1	2026-08-30	حاضر		2026-08-30 17:40:03.096855	\N
1608	16	1	1	1	2026-08-30	حاضر		2026-08-30 17:40:03.096855	\N
1609	3	1	1	1	2026-08-30	حاضر		2026-08-30 17:40:03.096855	\N
1610	13	1	1	1	2026-08-30	حاضر		2026-08-30 17:40:03.096855	\N
1611	17	1	1	1	2026-08-30	حاضر		2026-08-30 17:40:03.096855	\N
1612	4	1	1	1	2026-08-30	حاضر		2026-08-30 17:40:03.096855	\N
1613	11	1	1	1	2026-08-30	حاضر		2026-08-30 17:40:03.096855	\N
1614	15	1	1	1	2026-08-30	حاضر		2026-08-30 17:40:03.096855	\N
1615	5	1	1	1	2026-08-30	حاضر		2026-08-30 17:40:03.096855	\N
1616	8	1	1	1	2026-08-30	حاضر		2026-08-30 17:40:03.096855	\N
1697	693	1	1	1	2026-09-02	حاضر	ee	2026-09-02 02:03:01.928854	\N
1698	18	1	1	1	2026-09-02	غائب		2026-09-02 02:03:01.928854	\N
1699	14	1	1	1	2026-09-02	حاضر		2026-09-02 02:03:01.928854	\N
1700	6	1	1	1	2026-09-02	حاضر		2026-09-02 02:03:01.928854	\N
1701	7	1	1	1	2026-09-02	حاضر		2026-09-02 02:03:01.928854	\N
1702	10	1	1	1	2026-09-02	حاضر		2026-09-02 02:03:01.928854	\N
1703	12	1	1	1	2026-09-02	حاضر		2026-09-02 02:03:01.928854	\N
1704	16	1	1	1	2026-09-02	حاضر		2026-09-02 02:03:01.928854	\N
1705	3	1	1	1	2026-09-02	حاضر		2026-09-02 02:03:01.928854	\N
1706	13	1	1	1	2026-09-02	حاضر		2026-09-02 02:03:01.928854	\N
1707	17	1	1	1	2026-09-02	حاضر		2026-09-02 02:03:01.928854	\N
1708	11	1	1	1	2026-09-02	حاضر		2026-09-02 02:03:01.928854	\N
1709	4	1	1	1	2026-09-02	حاضر		2026-09-02 02:03:01.928854	\N
1710	15	1	1	1	2026-09-02	حاضر		2026-09-02 02:03:01.928854	\N
1711	5	1	1	1	2026-09-02	حاضر		2026-09-02 02:03:01.928854	\N
1712	8	1	1	1	2026-09-02	حاضر		2026-09-02 02:03:01.928854	\N
\.


--
-- Data for Name: employee_allowances_deductions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employee_allowances_deductions (id, employee_id, type, amount, reason, date, created_at, updated_at) FROM stdin;
1	5	خصم	10823.00		2026-08-17	2026-08-24 22:59:44.680752	\N
2	5	حافز	20905.00		2026-08-05	2026-08-24 22:59:44.680752	\N
3	6	بدل	23986.00	بدل مواصلات	2026-08-24	2026-08-24 22:59:44.680752	\N
4	7	غياب	6977.00	خصم غياب	2026-08-16	2026-08-24 22:59:44.680752	\N
5	7	مكافأة	24272.00		2026-08-12	2026-08-24 22:59:44.680752	\N
6	7	بدل	17444.00	بدل مواصلات	2026-07-28	2026-08-24 22:59:44.680752	\N
7	8	مكافأة	7952.00		2026-08-10	2026-08-24 22:59:44.680752	\N
8	9	خصم	21062.00		2026-07-25	2026-08-24 22:59:44.680752	\N
9	10	بدل	25407.00	بدل مواصلات	2026-07-14	2026-08-24 22:59:44.680752	\N
10	10	بدل	14497.00	بدل مواصلات	2026-08-06	2026-08-24 22:59:44.680752	\N
11	11	بدل	16867.00	بدل مواصلات	2026-08-08	2026-08-24 22:59:44.680752	\N
12	11	خصم	29265.00		2026-08-05	2026-08-24 22:59:44.680752	\N
13	12	مكافأة	21269.00		2026-07-18	2026-08-24 22:59:44.680752	\N
14	13	بدل	6662.00	بدل مواصلات	2026-07-14	2026-08-24 22:59:44.680752	\N
15	13	حافز	26325.00		2026-07-26	2026-08-24 22:59:44.680752	\N
16	13	حافز	25144.00		2026-08-19	2026-08-24 22:59:44.680752	\N
17	14	خصم	6480.00		2026-08-04	2026-08-24 22:59:44.680752	\N
18	14	غياب	12584.00	خصم غياب	2026-08-02	2026-08-24 22:59:44.680752	\N
19	14	خصم	22289.00		2026-08-13	2026-08-24 22:59:44.680752	\N
20	15	غياب	6206.00	خصم غياب	2026-07-27	2026-08-24 22:59:44.680752	\N
21	15	حافز	9403.00		2026-07-11	2026-08-24 22:59:44.680752	\N
22	15	مكافأة	11595.00		2026-07-22	2026-08-24 22:59:44.680752	\N
23	16	مكافأة	14202.00		2026-07-24	2026-08-24 22:59:44.680752	\N
24	17	مكافأة	24304.00		2026-07-18	2026-08-24 22:59:44.680752	\N
25	17	حافز	19423.00		2026-07-25	2026-08-24 22:59:44.680752	\N
26	18	بدل	21590.00	بدل مواصلات	2026-07-13	2026-08-24 22:59:44.680752	\N
27	19	بدل	8642.00	بدل مواصلات	2026-07-17	2026-08-24 22:59:44.680752	\N
28	19	حافز	11202.00		2026-08-18	2026-08-24 22:59:44.680752	\N
29	19	حافز	17381.00		2026-08-21	2026-08-24 22:59:44.680752	\N
\.


--
-- Data for Name: employee_loans; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employee_loans (id, employee_id, total_loan_amount, monthly_deduction, status, loan_date, reason, created_at, updated_at, remaining_amount) FROM stdin;
4	10	188008.00	20889.78	منتهية	2026-06-19	ظروف شخصية	2026-08-24 22:59:44.680752	\N	0.00
2	6	137964.00	45988.00	مستمرة	2026-06-23	ظروف شخصية	2026-08-24 22:59:44.680752	\N	137964.00
5	11	125041.00	31260.25	مستمرة	2026-05-17	ظروف شخصية	2026-08-24 22:59:44.680752	\N	125041.00
7	14	133859.00	16732.38	مستمرة	2026-06-12	ظروف شخصية	2026-08-24 22:59:44.680752	\N	133859.00
6	12	192665.00	21407.22	مستمرة	2026-06-18	ظروف شخصية	2026-08-24 22:59:44.680752	2026-09-02 03:53:25.745263	171257.78
3	7	55479.00	55555.00	مستمرة	2026-06-20	ظروف شخصية	2026-08-24 22:59:44.680752	2026-09-02 04:02:20.142295	55479.00
1	5	199703.00	16641.92	مستمرة	2026-06-21	ظروف شخصية	2026-08-24 22:59:44.680752	2026-09-02 04:05:23.973673	183061.08
8	5	20000.00	30000.00	منتهية	2026-09-01	\N	2026-09-01 05:32:33.618972	2026-09-02 04:05:23.973673	0.00
9	1	13.00	9.00	مستمرة	2026-09-02	\N	2026-09-02 04:07:06.16323	\N	13.00
\.


--
-- Data for Name: employees; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employees (id, full_name, job_title, qualification, primary_phone, secondary_phone, gender, marital_status, address, status, national_id, id_issue_place, id_issue_date, birth_date, birth_village, birth_district, birth_governorate, contract_start_date, contract_end_date, basic_salary, payment_method, bank_account_number, created_at, updated_at) FROM stdin;
1	مدير النظام	مدير نظام	\N	0000000000	\N	\N	\N	\N	نشط	\N	\N	\N	\N	\N	\N	\N	\N	\N	0.00	نقداً	\N	2026-08-21 02:18:55.612715	\N
10	سارة خالد النهاريr	معلم قرآن كريم	ماجستير	776688120	\N	أنثى	أعزب	الغربية	نشط	70739387	تعز	2010-06-26	1991-06-20	الشارع	الجنوبية	عدن	2020-09-01	2027-08-31	147433.00	حساب بنكي	\N	2026-08-24 22:59:44.680752	2026-08-27 01:36:35.469982
5	راشد علي الذماري	معلم تربية فنية	دبلوم	774216954	\N	ذكر	أعزب	الجنوبية	نشط	84942954	صنعاء	2011-04-26	1975-07-19	المنطقة	الجنوبية	صنعاء	2020-09-01	2027-08-31	111926.00	حساب بنكي	\N	2026-08-24 22:59:44.680752	\N
6	أمل ناصر الذماري	مدير عام	دبلوم	775475460	774480255	أنثى	أعزب	الشرقية	نشط	23001588	المكلا	2014-06-23	1984-11-16	المنطقة	الشرقية	ذمار	2020-09-01	2027-08-31	236904.00	حساب بنكي	\N	2026-08-24 22:59:44.680752	\N
7	محمود سامي الريمي	أمين مكتبة	ماجستير	779649914	\N	ذكر	أعزب	المدينة	إجازة	55442441	عدن	2023-08-07	1975-01-27	القرية	المدينة	ذمار	2020-09-01	2027-08-31	221906.00	نقداً	810176	2026-08-24 22:59:44.680752	\N
8	عبدالله عمر الشرعبي	محاسب	دبلوم	774986779	\N	ذكر	متزوج	المدينة	نشط	69454858	ذمار	2010-03-22	2000-08-25	الشارع	الشمالية	ذمار	2020-09-01	2027-08-31	227081.00	حساب بنكي	570705	2026-08-24 22:59:44.680752	\N
9	وليد طلال الشميري	مدير عام	ماجستير	777644337	\N	ذكر	أعزب	الشرقية	إجازة	72073300	الحديدة	2018-06-12	1987-01-18	المنطقة	المدينة	ذمار	2020-09-01	2027-08-31	119646.00	محفظة إلكترونية	537240	2026-08-24 22:59:44.680752	\N
11	زينب حسن العمراني	معلم رياضيات	دكتوراه	773750340	\N	أنثى	أعزب	الشرقية	نشط	89516702	صنعاء	2023-11-20	1984-02-05	القرية	المدينة	صنعاء	2020-09-01	2027-08-31	127427.00	نقداً	956109	2026-08-24 22:59:44.680752	\N
12	أحمد محمد العمراني	معلم تربية إسلامية	دبلوم	777824402	\N	ذكر	متزوج	الشمالية	نشط	43623265	ذمار	2013-08-26	1998-09-15	المنطقة	الشمالية	عدن	2020-09-01	2027-08-31	248985.00	محفظة إلكترونية	\N	2026-08-24 22:59:44.680752	\N
13	رنا يوسف الحضرمي	أخصائي اجتماعي	دبلوم	779125210	\N	أنثى	أعزب	الشمالية	نشط	64761132	تعز	2012-06-18	1984-02-15	الحي	المركز	صنعاء	2020-09-01	2027-08-31	128636.00	حساب بنكي	\N	2026-08-24 22:59:44.680752	\N
14	لينا إبراهيم العدني	مشرف تربوي	بكالوريوس	773614356	\N	أنثى	متزوج	الجنوبية	نشط	55776191	الحديدة	2023-10-17	1980-09-16	الحارة	المدينة	الحديدة	2020-09-01	2027-08-31	212050.00	حساب بنكي	632095	2026-08-24 22:59:44.680752	\N
15	مريم أحمد المخلافي	مدير عام	ماجستير	779781632	\N	أنثى	متزوج	المركز	نشط	60453791	تعز	2014-08-21	1994-02-13	المنطقة	الشمالية	إب	2020-09-01	2027-08-31	163636.00	نقداً	352155	2026-08-24 22:59:44.680752	\N
16	ماجد فهد المأربي	محاسب	بكالوريوس	774111844	770654173	ذكر	متزوج	الغربية	نشط	45571354	إب	2020-11-14	1999-02-12	الحي	المدينة	إب	2020-09-01	2027-08-31	123808.00	حساب بنكي	\N	2026-08-24 22:59:44.680752	\N
17	حسن يوسف الحمادي	أخصائي اجتماعي	دكتوراه	770261882	\N	ذكر	أعزب	المركز	إجازة	74586289	ذمار	2015-02-24	1986-04-19	الشارع	المركز	ذمار	2020-09-01	2027-08-31	146387.00	نقداً	\N	2026-08-24 22:59:44.680752	\N
18	ناصر عبدالعزيز الضالعي	معلم رياضيات	ماجستير	777864427	776923581	ذكر	متزوج	الجنوبية	نشط	16623346	حضرموت	2013-10-09	1975-12-12	الحي	المركز	حضرموت	2020-09-01	2027-08-31	100303.00	محفظة إلكترونية	\N	2026-08-24 22:59:44.680752	\N
19	أنس محمد الحدي	مدير عام	ماجستير	774277143	\N	ذكر	أعزب	الغربية	نشط	39081734	تعز	2014-11-18	1989-12-15	المنطقة	الشرقية	عدن	2020-09-01	2027-08-31	168836.00	نقداً	280251	2026-08-24 22:59:44.680752	\N
20	بسمة فهد الضالعي	معلم قرآن كريم	دكتوراه	776216900	\N	أنثى	أعزب	الشرقية	نشط	12498624	المكلا	2010-05-07	1981-12-01	الحارة	الشمالية	صنعاء	2020-09-01	2027-08-31	118026.00	محفظة إلكترونية	969637	2026-08-24 22:59:44.680752	\N
21	سلطان محمد الإبي	معلم لغة عربية	دكتوراه	775602193	\N	ذكر	أعزب	الغربية	إجازة	75451521	الحديدة	2018-10-19	1994-02-14	الشارع	الشمالية	المكلا	2020-09-01	2027-08-31	225401.00	محفظة إلكترونية	\N	2026-08-24 22:59:44.680752	\N
22	سعيد علي المخلافي	مدير عام	بكالوريوس	772793958	770404661	ذكر	أعزب	الشمالية	نشط	92491248	تعز	2023-02-05	2000-06-19	الشارع	المركز	الحديدة	2020-09-01	2027-08-31	97649.00	نقداً	813678	2026-08-24 22:59:44.680752	\N
23	فهد سعود العدني	محاسب	دكتوراه	772819815	\N	ذكر	أعزب	المركز	نشط	92143043	تعز	2010-09-16	1978-03-28	الشارع	الشمالية	صنعاء	2020-09-01	2027-08-31	117980.00	نقداً	916093	2026-08-24 22:59:44.680752	\N
24	بلال أحمد الرازحي	معلم قرآن كريم	ماجستير	772204493	775134637	ذكر	أعزب	الشرقية	نشط	76220938	المكلا	2015-06-04	1984-09-18	القرية	الشمالية	المكلا	2020-09-01	2027-08-31	169821.00	نقداً	406065	2026-08-24 22:59:44.680752	\N
25	زياد هشام العنسي	مدير عام	دكتوراه	776976877	773393930	ذكر	متزوج	المركز	نشط	12432883	عدن	2019-05-11	1986-10-09	الشارع	الشمالية	صنعاء	2020-09-01	2027-08-31	167367.00	حساب بنكي	175801	2026-08-24 22:59:44.680752	\N
26	فاطمة علي الشرعبي	معلم تربية بدنية	دبلوم	770741860	777247383	أنثى	متزوج	الشمالية	إجازة	99493073	الحديدة	2014-11-26	1992-11-03	الشارع	الغربية	الحديدة	2020-09-01	2027-08-31	155205.00	محفظة إلكترونية	\N	2026-08-24 22:59:44.680752	\N
27	طلال ناصر الحضرمي	مشرف تربوي	دبلوم	778500859	\N	ذكر	متزوج	الغربية	نشط	93678557	ذمار	2011-05-09	1994-03-12	المنطقة	الجنوبية	ذمار	2020-09-01	2027-08-31	197153.00	نقداً	477654	2026-08-24 22:59:44.680752	\N
28	بدر حمد الجوفي	مدير عام	بكالوريوس	770827183	\N	ذكر	متزوج	الجنوبية	نشط	40329063	تعز	2013-01-03	1987-09-22	الحارة	المدينة	تعز	2020-09-01	2027-08-31	173838.00	حساب بنكي	778941	2026-08-24 22:59:44.680752	\N
29	عائشة محمد الحكيمي	معلم رياضيات	دكتوراه	770975362	\N	أنثى	أعزب	المركز	نشط	25986312	الحديدة	2019-12-07	2000-09-20	القرية	المركز	تعز	2020-09-01	2027-08-31	213489.00	حساب بنكي	\N	2026-08-24 22:59:44.680752	\N
30	هدى سامي الإبي	معلم علوم	بكالوريوس	770433342	773619351	أنثى	متزوج	الغربية	نشط	28318526	إب	2015-07-28	1993-09-03	الحارة	الغربية	المكلا	2020-09-01	2027-08-31	129386.00	محفظة إلكترونية	\N	2026-08-24 22:59:44.680752	\N
31	خالد عبدالله الحكيمي	معلم تربية إسلامية	ماجستير	770846361	777571520	ذكر	أعزب	المركز	نشط	47571769	عدن	2014-03-12	1998-07-26	المنطقة	الشمالية	عدن	2020-09-01	2027-08-31	229136.00	حساب بنكي	714402	2026-08-24 22:59:44.680752	\N
33	نورة عبدالله الريمي	مدير عام	بكالوريوس	776793541	\N	أنثى	متزوج	المركز	إجازة	33466875	إب	2010-11-17	1996-09-13	المنطقة	الشمالية	المكلا	2020-09-01	2027-08-31	114749.00	محفظة إلكترونية	254709	2026-08-24 22:59:44.680752	\N
34	خديجة عمر الحمادي	ممرض	ماجستير	778162536	\N	أنثى	أعزب	المركز	نشط	57377303	حضرموت	2021-03-20	1981-03-05	الشارع	الجنوبية	حضرموت	2020-09-01	2027-08-31	170565.00	حساب بنكي	\N	2026-08-24 22:59:44.680752	\N
32	إبراهيم خليل النهاريd	أخصائي اجتماعي	دكتوراه	778766154	\N	ذكر	أعزب	الغربية	نشط	42144210	ذمار	2018-06-22	1987-02-28	القرية	الجنوبية	المكلا	2020-09-01	2027-08-31	91759.00	نقداً	32	2026-08-24 22:59:44.680752	2026-08-27 01:34:47.613045
\.


--
-- Data for Name: expense_vouchers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expense_vouchers (id, voucher_number, expense_category, beneficiary_name, amount, payment_date, payment_method, invoice_number, notes, created_by_user_id, status, cancellation_reason, cancelled_at, created_at, updated_at) FROM stdin;
1	EXP-01-00001	مشتريات مواد	مؤسسة النظافة	13980.00	2026-08-05 22:59:48.836899	تحويل بنكي	\N	فعالية مدرسية	1	ملغى	إلغاء	\N	2026-08-24 22:59:44.680752	\N
2	EXP-01-00002	أخرى	مكتبة النور	106221.00	2026-08-21 22:59:48.836978	نقداً	INV-6377	فعالية مدرسية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
3	EXP-01-00003	أنشطة مدرسية	شركة النقل	29390.00	2026-08-02 22:59:48.837016	تحويل بنكي	\N	صيانة دورية	1	نشط	إلغاء	\N	2026-08-24 22:59:44.680752	\N
4	EXP-01-00004	فعاليات واحتفالات	شركة النقل	64160.00	2026-07-07 22:59:48.837044	تحويل بنكي	INV-4096	شراء مستلزمات	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
5	EXP-01-00005	فعاليات واحتفالات	مكتبة النور	106791.00	2026-06-14 22:59:48.837072	نقداً	\N	صيانة دورية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
6	EXP-01-00006	أخرى	مكتبة النور	107006.00	2026-05-26 22:59:48.8371	تحويل بنكي	\N	صيانة دورية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
7	EXP-01-00007	أخرى	مؤسسة النظافة	90331.00	2026-06-14 22:59:48.837124	تحويل بنكي	\N		1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
8	EXP-01-00008	فعاليات واحتفالات	شركة التقنية	14706.00	2026-07-15 22:59:48.83715	تحويل بنكي	\N	صيانة دورية	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
9	EXP-01-00009	مشتريات مواد	مكتبة النور	120201.00	2026-06-01 22:59:48.837174	نقداً	\N		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
10	EXP-01-00010	فعاليات واحتفالات	مؤسسة النظافة	107496.00	2026-06-24 22:59:48.837198	تحويل بنكي	INV-9820	شراء مستلزمات	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
11	EXP-01-00011	فعاليات واحتفالات	شركة التقنية	124049.00	2026-07-21 22:59:48.837223	تحويل بنكي	INV-7232	فعالية مدرسية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
12	EXP-01-00012	أنشطة مدرسية	شركة النقل	87810.00	2026-06-08 22:59:48.837247	تحويل بنكي	\N	صيانة دورية	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
13	EXP-01-00013	أخرى	شركة النقل	135286.00	2026-07-07 22:59:48.83727	نقداً	\N	صيانة دورية	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
14	EXP-01-00014	مشتريات مواد	شركة التقنية	19735.00	2026-06-12 22:59:48.837294	تحويل بنكي	\N	شراء مستلزمات	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
15	EXP-01-00015	أنشطة مدرسية	مطعم المدرسة	84535.00	2026-06-13 22:59:48.837317	نقداً	\N		1	ملغى	إلغاء	\N	2026-08-24 22:59:44.680752	\N
16	EXP-01-00016	أنشطة مدرسية	مكتبة النور	88843.00	2026-08-03 22:59:48.837339	تحويل بنكي	INV-4427	فعالية مدرسية	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
17	EXP-01-00017	أنشطة مدرسية	مكتبة النور	125549.00	2026-05-29 22:59:48.837363	نقداً	\N		1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
18	EXP-01-00018	فعاليات واحتفالات	شركة النقل	97934.00	2026-06-12 22:59:48.837386	نقداً	\N	صيانة دورية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
19	EXP-01-00019	أنشطة مدرسية	مكتبة النور	15702.00	2026-05-26 22:59:48.837408	تحويل بنكي	\N		1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
20	EXP-01-00020	أخرى	مكتبة النور	146239.00	2026-05-30 22:59:48.83743	نقداً	\N	صيانة دورية	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
21	EXP-01-00021	مشتريات مواد	مؤسسة النظافة	70358.00	2026-08-02 22:59:48.837453	نقداً	\N	فعالية مدرسية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
22	EXP-01-00022	أخرى	مطعم المدرسة	130809.00	2026-06-30 22:59:48.837477	نقداً	INV-1398	شراء مستلزمات	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
23	EXP-01-00023	أخرى	مؤسسة النظافة	105985.00	2026-07-24 22:59:48.837501	تحويل بنكي	\N	فعالية مدرسية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
24	EXP-01-00024	فعاليات واحتفالات	مكتبة النور	86158.00	2026-07-12 22:59:48.837524	نقداً	INV-6202	شراء مستلزمات	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
25	EXP-01-00025	أخرى	شركة التقنية	95411.00	2026-07-20 22:59:48.837548	تحويل بنكي	\N	فعالية مدرسية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
26	EXP-01-00026	أخرى	مطعم المدرسة	103708.00	2026-06-08 22:59:48.83757	نقداً	INV-9271	فعالية مدرسية	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
28	EXP-01-00028	أخرى	شركة النقل	117601.00	2026-06-11 22:59:48.837623	نقداً	\N	صيانة دورية	1	نشط	إلغاء	\N	2026-08-24 22:59:44.680752	\N
29	EXP-01-00029	فعاليات واحتفالات	مطعم المدرسة	103667.00	2026-08-07 22:59:48.837647	نقداً	INV-7681	فعالية مدرسية	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
30	EXP-01-00030	أنشطة مدرسية	مطعم المدرسة	141189.00	2026-06-20 22:59:48.837671	تحويل بنكي	INV-6266		1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
31	EXP-01-00031	صيانة وتشغيل	مطعم المدرسة	40757.00	2026-06-13 22:59:48.837696	نقداً	INV-5164	شراء مستلزمات	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
32	EXP-01-00032	أنشطة مدرسية	مؤسسة النظافة	88090.00	2026-07-31 22:59:48.837719	تحويل بنكي	\N	فعالية مدرسية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
33	EXP-01-00033	أنشطة مدرسية	شركة النقل	52892.00	2026-08-13 22:59:48.837742	تحويل بنكي	\N		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
34	EXP-01-00034	أنشطة مدرسية	مكتبة النور	55010.00	2026-06-01 22:59:48.837765	تحويل بنكي	INV-5448		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
35	EXP-01-00035	مشتريات مواد	شركة النقل	58072.00	2026-07-24 22:59:48.83779	تحويل بنكي	\N	شراء مستلزمات	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
37	EXP-01-00037	صيانة وتشغيل	مكتبة النور	25665.00	2026-07-02 22:59:48.837836	تحويل بنكي	\N	شراء مستلزمات	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
38	EXP-01-00038	فعاليات واحتفالات	شركة النقل	149333.00	2026-06-09 22:59:48.837858	نقداً	INV-7632		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
39	EXP-01-00039	أنشطة مدرسية	مطعم المدرسة	103830.00	2026-06-21 22:59:48.837881	نقداً	\N	صيانة دورية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
40	EXP-01-00040	مشتريات مواد	مؤسسة النظافة	135609.00	2026-06-16 22:59:48.837904	نقداً	\N	صيانة دورية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
27	EXP-01-00027	صيانة وتشغيل	شركة التقنية	126729.00	2026-08-17 22:59:48.837596	تحويل بنكي	INV-3360	شراء مستلزمات	2	نشط	\N	\N	2026-08-24 22:59:44.680752	2026-08-25 04:45:15.834686
36	EXP-01-00036	أخرى	مطعم المدرسة	50624.00	2026-08-21 22:59:48.837813	تحويل بنكي	INV-1185	صيانة دورية	2	نشط	إلغاء يدوي	2026-08-25 04:07:39.651233	2026-08-24 22:59:44.680752	2026-09-01 04:53:52.900566
\.


--
-- Data for Name: fee_installments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fee_installments (id, student_fee_id, installment_type, installment_number, installment_name, amount, due_date, is_paid, paid_amount, created_at, updated_at) FROM stdin;
1	1	regular	1	قسط 1	-588.50	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
2	1	regular	2	قسط 2	-588.50	2026-11-15	t	-588.50	2026-08-24 22:59:44.680752	\N
3	2	regular	1	قسط 1	181527.50	2026-09-15	t	181527.50	2026-08-24 22:59:44.680752	\N
4	2	regular	2	قسط 2	181527.50	2026-11-15	t	181527.50	2026-08-24 22:59:44.680752	\N
9	5	regular	1	قسط 1	177237.50	2026-09-15	t	177237.50	2026-08-24 22:59:44.680752	\N
10	5	regular	2	قسط 2	177237.50	2026-11-15	t	177237.50	2026-08-24 22:59:44.680752	\N
11	6	regular	1	قسط 1	119514.33	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
12	6	regular	2	قسط 2	119514.33	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
13	6	regular	3	قسط 3	119514.33	2027-01-15	t	119514.33	2026-08-24 22:59:44.680752	\N
14	7	regular	1	قسط 1	90702.25	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
15	7	regular	2	قسط 2	90702.25	2026-11-15	t	90702.25	2026-08-24 22:59:44.680752	\N
16	7	regular	3	قسط 3	90702.25	2027-01-15	t	90702.25	2026-08-24 22:59:44.680752	\N
17	7	regular	4	قسط 4	90702.25	2027-03-15	f	0.00	2026-08-24 22:59:44.680752	\N
18	8	regular	1	قسط 1	184984.00	2026-09-15	t	184984.00	2026-08-24 22:59:44.680752	\N
19	8	regular	2	قسط 2	184984.00	2026-11-15	t	184984.00	2026-08-24 22:59:44.680752	\N
20	9	regular	1	قسط 1	89196.00	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
21	9	regular	2	قسط 2	89196.00	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
22	9	regular	3	قسط 3	89196.00	2027-01-15	f	0.00	2026-08-24 22:59:44.680752	\N
23	9	regular	4	قسط 4	89196.00	2027-03-15	f	0.00	2026-08-24 22:59:44.680752	\N
24	10	regular	1	قسط 1	92197.50	2026-09-15	t	92197.50	2026-08-24 22:59:44.680752	\N
25	10	regular	2	قسط 2	92197.50	2026-11-15	t	92197.50	2026-08-24 22:59:44.680752	\N
26	10	regular	3	قسط 3	92197.50	2027-01-15	t	92197.50	2026-08-24 22:59:44.680752	\N
27	10	regular	4	قسط 4	92197.50	2027-03-15	t	92197.50	2026-08-24 22:59:44.680752	\N
28	11	regular	1	قسط 1	89758.25	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
29	11	regular	2	قسط 2	89758.25	2026-11-15	t	89758.25	2026-08-24 22:59:44.680752	\N
30	11	regular	3	قسط 3	89758.25	2027-01-15	f	0.00	2026-08-24 22:59:44.680752	\N
31	11	regular	4	قسط 4	89758.25	2027-03-15	t	89758.25	2026-08-24 22:59:44.680752	\N
32	12	regular	1	قسط 1	90712.50	2026-09-15	t	90712.50	2026-08-24 22:59:44.680752	\N
33	12	regular	2	قسط 2	90712.50	2026-11-15	t	90712.50	2026-08-24 22:59:44.680752	\N
34	12	regular	3	قسط 3	90712.50	2027-01-15	t	90712.50	2026-08-24 22:59:44.680752	\N
35	12	regular	4	قسط 4	90712.50	2027-03-15	t	90712.50	2026-08-24 22:59:44.680752	\N
36	13	regular	1	قسط 1	90841.25	2026-09-15	t	90841.25	2026-08-24 22:59:44.680752	\N
37	13	regular	2	قسط 2	90841.25	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
38	13	regular	3	قسط 3	90841.25	2027-01-15	f	0.00	2026-08-24 22:59:44.680752	\N
39	13	regular	4	قسط 4	90841.25	2027-03-15	f	0.00	2026-08-24 22:59:44.680752	\N
40	14	regular	1	قسط 1	183371.50	2026-09-15	t	183371.50	2026-08-24 22:59:44.680752	\N
41	14	regular	2	قسط 2	183371.50	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
42	15	previous_debt	0	قسط رصيد سابقة مرحّل	7073.00	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
43	15	regular	1	قسط 1	184784.00	2026-09-15	t	184784.00	2026-08-24 22:59:44.680752	\N
44	15	regular	2	قسط 2	184784.00	2026-11-15	t	184784.00	2026-08-24 22:59:44.680752	\N
45	16	regular	1	قسط 1	118393.00	2026-09-15	t	118393.00	2026-08-24 22:59:44.680752	\N
46	16	regular	2	قسط 2	118393.00	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
47	16	regular	3	قسط 3	118393.00	2027-01-15	t	118393.00	2026-08-24 22:59:44.680752	\N
48	17	regular	1	قسط 1	124064.33	2026-09-15	t	124064.33	2026-08-24 22:59:44.680752	\N
49	17	regular	2	قسط 2	124064.33	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
50	17	regular	3	قسط 3	124064.33	2027-01-15	t	124064.33	2026-08-24 22:59:44.680752	\N
51	18	previous_debt	0	قسط رصيد سابقة مرحّل	3447.00	2026-09-15	t	0.00	2026-08-24 22:59:44.680752	\N
52	18	regular	1	قسط 1	89793.75	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
53	18	regular	2	قسط 2	89793.75	2026-11-15	t	89793.75	2026-08-24 22:59:44.680752	\N
54	18	regular	3	قسط 3	89793.75	2027-01-15	f	0.00	2026-08-24 22:59:44.680752	\N
55	18	regular	4	قسط 4	89793.75	2027-03-15	t	89793.75	2026-08-24 22:59:44.680752	\N
56	19	previous_debt	0	قسط رصيد سابقة مرحّل	30940.00	2026-09-15	t	30940.00	2026-08-24 22:59:44.680752	\N
57	19	regular	1	قسط 1	118602.33	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
58	19	regular	2	قسط 2	118602.33	2026-11-15	t	118602.33	2026-08-24 22:59:44.680752	\N
59	19	regular	3	قسط 3	118602.33	2027-01-15	f	0.00	2026-08-24 22:59:44.680752	\N
60	20	regular	1	قسط 1	182963.50	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
61	20	regular	2	قسط 2	182963.50	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
62	21	regular	1	قسط 1	89927.25	2026-09-15	t	89927.25	2026-08-24 22:59:44.680752	\N
63	21	regular	2	قسط 2	89927.25	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
64	21	regular	3	قسط 3	89927.25	2027-01-15	f	0.00	2026-08-24 22:59:44.680752	\N
65	21	regular	4	قسط 4	89927.25	2027-03-15	f	0.00	2026-08-24 22:59:44.680752	\N
66	22	previous_debt	0	قسط رصيد سابقة مرحّل	28411.00	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
67	22	regular	1	قسط 1	89679.00	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
68	22	regular	2	قسط 2	89679.00	2026-11-15	t	89679.00	2026-08-24 22:59:44.680752	\N
69	22	regular	3	قسط 3	89679.00	2027-01-15	t	89679.00	2026-08-24 22:59:44.680752	\N
70	22	regular	4	قسط 4	89679.00	2027-03-15	f	0.00	2026-08-24 22:59:44.680752	\N
71	23	previous_debt	0	قسط رصيد سابقة مرحّل	14465.00	2026-09-15	t	0.00	2026-08-24 22:59:44.680752	\N
72	23	regular	1	قسط 1	181213.00	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
73	23	regular	2	قسط 2	181213.00	2026-11-15	t	181213.00	2026-08-24 22:59:44.680752	\N
74	24	previous_debt	0	قسط رصيد سابقة مرحّل	25686.00	2026-09-15	t	0.00	2026-08-24 22:59:44.680752	\N
75	24	regular	1	قسط 1	118388.00	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
76	24	regular	2	قسط 2	118388.00	2026-11-15	t	118388.00	2026-08-24 22:59:44.680752	\N
77	24	regular	3	قسط 3	118388.00	2027-01-15	f	0.00	2026-08-24 22:59:44.680752	\N
78	25	regular	1	قسط 1	186674.50	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
79	25	regular	2	قسط 2	186674.50	2026-11-15	t	186674.50	2026-08-24 22:59:44.680752	\N
80	26	regular	1	قسط 1	180123.00	2026-09-15	t	180123.00	2026-08-24 22:59:44.680752	\N
81	26	regular	2	قسط 2	180123.00	2026-11-15	t	180123.00	2026-08-24 22:59:44.680752	\N
82	27	previous_debt	0	قسط رصيد سابقة مرحّل	2679.00	2026-09-15	t	2679.00	2026-08-24 22:59:44.680752	\N
83	27	regular	1	قسط 1	118806.33	2026-09-15	t	118806.33	2026-08-24 22:59:44.680752	\N
84	27	regular	2	قسط 2	118806.33	2026-11-15	t	118806.33	2026-08-24 22:59:44.680752	\N
85	27	regular	3	قسط 3	118806.33	2027-01-15	t	118806.33	2026-08-24 22:59:44.680752	\N
86	28	regular	1	قسط 1	180199.50	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
87	28	regular	2	قسط 2	180199.50	2026-11-15	t	180199.50	2026-08-24 22:59:44.680752	\N
88	29	regular	1	قسط 1	92487.75	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
89	29	regular	2	قسط 2	92487.75	2026-11-15	t	92487.75	2026-08-24 22:59:44.680752	\N
90	29	regular	3	قسط 3	92487.75	2027-01-15	t	92487.75	2026-08-24 22:59:44.680752	\N
91	29	regular	4	قسط 4	92487.75	2027-03-15	t	92487.75	2026-08-24 22:59:44.680752	\N
92	30	regular	1	قسط 1	90201.25	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
93	30	regular	2	قسط 2	90201.25	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
94	30	regular	3	قسط 3	90201.25	2027-01-15	t	90201.25	2026-08-24 22:59:44.680752	\N
95	30	regular	4	قسط 4	90201.25	2027-03-15	f	0.00	2026-08-24 22:59:44.680752	\N
96	31	previous_debt	0	قسط رصيد سابقة مرحّل	7195.00	2026-09-15	t	7195.00	2026-08-24 22:59:44.680752	\N
97	31	regular	1	قسط 1	179930.50	2026-09-15	t	179930.50	2026-08-24 22:59:44.680752	\N
98	31	regular	2	قسط 2	179930.50	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
99	32	regular	1	قسط 1	177593.50	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
100	32	regular	2	قسط 2	177593.50	2026-11-15	t	177593.50	2026-08-24 22:59:44.680752	\N
101	33	regular	1	قسط 1	123679.67	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
102	33	regular	2	قسط 2	123679.67	2026-11-15	t	123679.67	2026-08-24 22:59:44.680752	\N
103	33	regular	3	قسط 3	123679.67	2027-01-15	f	0.00	2026-08-24 22:59:44.680752	\N
104	34	previous_debt	0	قسط رصيد سابقة مرحّل	44934.00	2026-09-15	t	44934.00	2026-08-24 22:59:44.680752	\N
105	34	regular	1	قسط 1	122542.33	2026-09-15	t	122542.33	2026-08-24 22:59:44.680752	\N
106	34	regular	2	قسط 2	122542.33	2026-11-15	t	122542.33	2026-08-24 22:59:44.680752	\N
107	34	regular	3	قسط 3	122542.33	2027-01-15	f	0.00	2026-08-24 22:59:44.680752	\N
108	35	regular	1	قسط 1	123123.00	2026-09-15	t	123123.00	2026-08-24 22:59:44.680752	\N
109	35	regular	2	قسط 2	123123.00	2026-11-15	t	123123.00	2026-08-24 22:59:44.680752	\N
110	35	regular	3	قسط 3	123123.00	2027-01-15	t	123123.00	2026-08-24 22:59:44.680752	\N
111	36	regular	1	قسط 1	123804.33	2026-09-15	t	123804.33	2026-08-24 22:59:44.680752	\N
112	36	regular	2	قسط 2	123804.33	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
113	36	regular	3	قسط 3	123804.33	2027-01-15	t	123804.33	2026-08-24 22:59:44.680752	\N
114	37	regular	1	قسط 1	118416.00	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
115	37	regular	2	قسط 2	118416.00	2026-11-15	t	118416.00	2026-08-24 22:59:44.680752	\N
116	37	regular	3	قسط 3	118416.00	2027-01-15	f	0.00	2026-08-24 22:59:44.680752	\N
117	38	previous_debt	0	قسط رصيد سابقة مرحّل	12308.00	2026-09-15	f	12308.00	2026-08-24 22:59:44.680752	\N
118	38	regular	1	قسط 1	121158.67	2026-09-15	t	121158.67	2026-08-24 22:59:44.680752	\N
119	38	regular	2	قسط 2	121158.67	2026-11-15	t	121158.67	2026-08-24 22:59:44.680752	\N
120	38	regular	3	قسط 3	121158.67	2027-01-15	t	121158.67	2026-08-24 22:59:44.680752	\N
121	39	regular	1	قسط 1	120811.33	2026-09-15	t	120811.33	2026-08-24 22:59:44.680752	\N
122	39	regular	2	قسط 2	120811.33	2026-11-15	t	120811.33	2026-08-24 22:59:44.680752	\N
123	39	regular	3	قسط 3	120811.33	2027-01-15	t	120811.33	2026-08-24 22:59:44.680752	\N
124	40	regular	1	قسط 1	90748.00	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
125	40	regular	2	قسط 2	90748.00	2026-11-15	t	90748.00	2026-08-24 22:59:44.680752	\N
126	40	regular	3	قسط 3	90748.00	2027-01-15	t	90748.00	2026-08-24 22:59:44.680752	\N
127	40	regular	4	قسط 4	90748.00	2027-03-15	t	90748.00	2026-08-24 22:59:44.680752	\N
128	41	regular	1	قسط 1	186030.00	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
129	41	regular	2	قسط 2	186030.00	2026-11-15	t	186030.00	2026-08-24 22:59:44.680752	\N
130	42	previous_debt	0	قسط رصيد سابقة مرحّل	43242.00	2026-09-15	t	0.00	2026-08-24 22:59:44.680752	\N
131	42	regular	1	قسط 1	186285.50	2026-09-15	t	186285.50	2026-08-24 22:59:44.680752	\N
132	42	regular	2	قسط 2	186285.50	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
133	43	previous_debt	0	قسط رصيد سابقة مرحّل	23348.00	2026-09-15	t	0.00	2026-08-24 22:59:44.680752	\N
134	43	regular	1	قسط 1	124105.33	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
135	43	regular	2	قسط 2	124105.33	2026-11-15	t	124105.33	2026-08-24 22:59:44.680752	\N
136	43	regular	3	قسط 3	124105.33	2027-01-15	f	0.00	2026-08-24 22:59:44.680752	\N
137	44	regular	1	قسط 1	90893.75	2026-09-15	t	90893.75	2026-08-24 22:59:44.680752	\N
138	44	regular	2	قسط 2	90893.75	2026-11-15	t	90893.75	2026-08-24 22:59:44.680752	\N
139	44	regular	3	قسط 3	90893.75	2027-01-15	t	90893.75	2026-08-24 22:59:44.680752	\N
140	44	regular	4	قسط 4	90893.75	2027-03-15	t	90893.75	2026-08-24 22:59:44.680752	\N
141	45	regular	1	قسط 1	179206.00	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
142	45	regular	2	قسط 2	179206.00	2026-11-15	t	179206.00	2026-08-24 22:59:44.680752	\N
143	46	regular	1	قسط 1	178831.50	2026-09-15	t	178831.50	2026-08-24 22:59:44.680752	\N
144	46	regular	2	قسط 2	178831.50	2026-11-15	t	178831.50	2026-08-24 22:59:44.680752	\N
145	47	regular	1	قسط 1	184238.50	2026-09-15	t	184238.50	2026-08-24 22:59:44.680752	\N
146	47	regular	2	قسط 2	184238.50	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
147	48	regular	1	قسط 1	90959.50	2026-09-15	t	90959.50	2026-08-24 22:59:44.680752	\N
148	48	regular	2	قسط 2	90959.50	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
149	48	regular	3	قسط 3	90959.50	2027-01-15	f	0.00	2026-08-24 22:59:44.680752	\N
150	48	regular	4	قسط 4	90959.50	2027-03-15	f	0.00	2026-08-24 22:59:44.680752	\N
151	49	previous_debt	0	قسط رصيد سابقة مرحّل	8539.00	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
152	49	regular	1	قسط 1	90765.25	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
153	49	regular	2	قسط 2	90765.25	2026-11-15	t	90765.25	2026-08-24 22:59:44.680752	\N
154	49	regular	3	قسط 3	90765.25	2027-01-15	t	90765.25	2026-08-24 22:59:44.680752	\N
155	49	regular	4	قسط 4	90765.25	2027-03-15	f	0.00	2026-08-24 22:59:44.680752	\N
156	50	previous_debt	0	قسط رصيد سابقة مرحّل	3071.00	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
157	50	regular	1	قسط 1	120937.67	2026-09-15	t	120937.67	2026-08-24 22:59:44.680752	\N
158	50	regular	2	قسط 2	120937.67	2026-11-15	t	120937.67	2026-08-24 22:59:44.680752	\N
159	50	regular	3	قسط 3	120937.67	2027-01-15	t	120937.67	2026-08-24 22:59:44.680752	\N
160	51	previous_debt	0	قسط رصيد سابقة مرحّل	35299.00	2026-09-15	t	0.00	2026-08-24 22:59:44.680752	\N
161	51	regular	1	قسط 1	194115.50	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
162	51	regular	2	قسط 2	194115.50	2026-11-15	t	194115.50	2026-08-24 22:59:44.680752	\N
163	52	previous_debt	0	قسط رصيد سابقة مرحّل	26175.00	2026-09-15	t	0.00	2026-08-24 22:59:44.680752	\N
164	52	regular	1	قسط 1	100234.50	2026-09-15	t	100234.50	2026-08-24 22:59:44.680752	\N
165	52	regular	2	قسط 2	100234.50	2026-11-15	t	100234.50	2026-08-24 22:59:44.680752	\N
166	52	regular	3	قسط 3	100234.50	2027-01-15	f	0.00	2026-08-24 22:59:44.680752	\N
167	52	regular	4	قسط 4	100234.50	2027-03-15	t	100234.50	2026-08-24 22:59:44.680752	\N
168	53	regular	1	قسط 1	203284.50	2026-09-15	t	203284.50	2026-08-24 22:59:44.680752	\N
169	53	regular	2	قسط 2	203284.50	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
170	54	regular	1	قسط 1	198585.50	2026-09-15	t	198585.50	2026-08-24 22:59:44.680752	\N
171	54	regular	2	قسط 2	198585.50	2026-11-15	t	198585.50	2026-08-24 22:59:44.680752	\N
172	55	regular	1	قسط 1	101749.50	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
173	55	regular	2	قسط 2	101749.50	2026-11-15	t	101749.50	2026-08-24 22:59:44.680752	\N
174	55	regular	3	قسط 3	101749.50	2027-01-15	t	101749.50	2026-08-24 22:59:44.680752	\N
175	55	regular	4	قسط 4	101749.50	2027-03-15	f	0.00	2026-08-24 22:59:44.680752	\N
176	56	previous_debt	0	قسط رصيد سابقة مرحّل	7441.00	2026-09-15	t	0.00	2026-08-24 22:59:44.680752	\N
177	56	regular	1	قسط 1	133565.33	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
178	56	regular	2	قسط 2	133565.33	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
179	56	regular	3	قسط 3	133565.33	2027-01-15	f	0.00	2026-08-24 22:59:44.680752	\N
180	57	regular	1	قسط 1	130375.00	2026-09-15	t	130375.00	2026-08-24 22:59:44.680752	\N
181	57	regular	2	قسط 2	130375.00	2026-11-15	t	130375.00	2026-08-24 22:59:44.680752	\N
182	57	regular	3	قسط 3	130375.00	2027-01-15	f	0.00	2026-08-24 22:59:44.680752	\N
183	58	regular	1	قسط 1	100892.75	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
184	58	regular	2	قسط 2	100892.75	2026-11-15	t	100892.75	2026-08-24 22:59:44.680752	\N
185	58	regular	3	قسط 3	100892.75	2027-01-15	f	0.00	2026-08-24 22:59:44.680752	\N
186	58	regular	4	قسط 4	100892.75	2027-03-15	f	0.00	2026-08-24 22:59:44.680752	\N
187	59	regular	1	قسط 1	99663.50	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
188	59	regular	2	قسط 2	99663.50	2026-11-15	t	99663.50	2026-08-24 22:59:44.680752	\N
189	59	regular	3	قسط 3	99663.50	2027-01-15	f	0.00	2026-08-24 22:59:44.680752	\N
190	59	regular	4	قسط 4	99663.50	2027-03-15	t	99663.50	2026-08-24 22:59:44.680752	\N
191	60	previous_debt	0	قسط رصيد سابقة مرحّل	18198.00	2026-09-15	t	0.00	2026-08-24 22:59:44.680752	\N
192	60	regular	1	قسط 1	134107.67	2026-09-15	t	134107.67	2026-08-24 22:59:44.680752	\N
193	60	regular	2	قسط 2	134107.67	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
194	60	regular	3	قسط 3	134107.67	2027-01-15	f	0.00	2026-08-24 22:59:44.680752	\N
195	61	regular	1	قسط 1	97904.25	2026-09-15	t	97904.25	2026-08-24 22:59:44.680752	\N
196	61	regular	2	قسط 2	97904.25	2026-11-15	t	97904.25	2026-08-24 22:59:44.680752	\N
197	61	regular	3	قسط 3	97904.25	2027-01-15	t	97904.25	2026-08-24 22:59:44.680752	\N
198	61	regular	4	قسط 4	97904.25	2027-03-15	t	97904.25	2026-08-24 22:59:44.680752	\N
199	62	regular	1	قسط 1	129589.00	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
200	62	regular	2	قسط 2	129589.00	2026-11-15	t	129589.00	2026-08-24 22:59:44.680752	\N
201	62	regular	3	قسط 3	129589.00	2027-01-15	t	129589.00	2026-08-24 22:59:44.680752	\N
202	63	regular	1	قسط 1	132333.33	2026-09-15	t	132333.33	2026-08-24 22:59:44.680752	\N
203	63	regular	2	قسط 2	132333.33	2026-11-15	t	132333.33	2026-08-24 22:59:44.680752	\N
204	63	regular	3	قسط 3	132333.33	2027-01-15	f	0.00	2026-08-24 22:59:44.680752	\N
205	64	previous_debt	0	قسط رصيد سابقة مرحّل	36294.00	2026-09-15	t	36294.00	2026-08-24 22:59:44.680752	\N
206	64	regular	1	قسط 1	200243.00	2026-09-15	t	200243.00	2026-08-24 22:59:44.680752	\N
207	64	regular	2	قسط 2	200243.00	2026-11-15	t	200243.00	2026-08-24 22:59:44.680752	\N
208	65	previous_debt	0	قسط رصيد سابقة مرحّل	47223.00	2026-09-15	t	0.00	2026-08-24 22:59:44.680752	\N
209	65	regular	1	قسط 1	99624.25	2026-09-15	t	99624.25	2026-08-24 22:59:44.680752	\N
210	65	regular	2	قسط 2	99624.25	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
211	65	regular	3	قسط 3	99624.25	2027-01-15	f	0.00	2026-08-24 22:59:44.680752	\N
212	65	regular	4	قسط 4	99624.25	2027-03-15	t	99624.25	2026-08-24 22:59:44.680752	\N
213	66	regular	1	قسط 1	197400.00	2026-09-15	t	197400.00	2026-08-24 22:59:44.680752	\N
214	66	regular	2	قسط 2	197400.00	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
215	67	previous_debt	0	قسط رصيد سابقة مرحّل	3121.00	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
216	67	regular	1	قسط 1	199220.50	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
217	67	regular	2	قسط 2	199220.50	2026-11-15	t	199220.50	2026-08-24 22:59:44.680752	\N
218	68	previous_debt	0	قسط رصيد سابقة مرحّل	48422.00	2026-09-15	t	0.00	2026-08-24 22:59:44.680752	\N
219	68	regular	1	قسط 1	130978.00	2026-09-15	t	130978.00	2026-08-24 22:59:44.680752	\N
220	68	regular	2	قسط 2	130978.00	2026-11-15	t	130978.00	2026-08-24 22:59:44.680752	\N
221	68	regular	3	قسط 3	130978.00	2027-01-15	t	130978.00	2026-08-24 22:59:44.680752	\N
222	69	previous_debt	0	قسط رصيد سابقة مرحّل	44607.00	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
223	69	regular	1	قسط 1	199108.50	2026-09-15	t	199108.50	2026-08-24 22:59:44.680752	\N
224	69	regular	2	قسط 2	199108.50	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
225	70	regular	1	قسط 1	97660.50	2026-09-15	t	97660.50	2026-08-24 22:59:44.680752	\N
226	70	regular	2	قسط 2	97660.50	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
227	70	regular	3	قسط 3	97660.50	2027-01-15	t	97660.50	2026-08-24 22:59:44.680752	\N
228	70	regular	4	قسط 4	97660.50	2027-03-15	t	97660.50	2026-08-24 22:59:44.680752	\N
229	71	regular	1	قسط 1	201791.50	2026-09-15	t	201791.50	2026-08-24 22:59:44.680752	\N
230	71	regular	2	قسط 2	201791.50	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
231	72	regular	1	قسط 1	196254.00	2026-09-15	t	196254.00	2026-08-24 22:59:44.680752	\N
232	72	regular	2	قسط 2	196254.00	2026-11-15	t	196254.00	2026-08-24 22:59:44.680752	\N
233	73	regular	1	قسط 1	201281.00	2026-09-15	t	201281.00	2026-08-24 22:59:44.680752	\N
234	73	regular	2	قسط 2	201281.00	2026-11-15	t	201281.00	2026-08-24 22:59:44.680752	\N
235	74	regular	1	قسط 1	129576.67	2026-09-15	t	129576.67	2026-08-24 22:59:44.680752	\N
236	74	regular	2	قسط 2	129576.67	2026-11-15	t	129576.67	2026-08-24 22:59:44.680752	\N
237	74	regular	3	قسط 3	129576.67	2027-01-15	t	129576.67	2026-08-24 22:59:44.680752	\N
238	75	previous_debt	0	قسط رصيد سابقة مرحّل	30801.00	2026-09-15	f	30801.00	2026-08-24 22:59:44.680752	\N
239	75	regular	1	قسط 1	135007.67	2026-09-15	t	135007.67	2026-08-24 22:59:44.680752	\N
240	75	regular	2	قسط 2	135007.67	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
241	75	regular	3	قسط 3	135007.67	2027-01-15	f	0.00	2026-08-24 22:59:44.680752	\N
242	76	regular	1	قسط 1	198788.00	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
243	76	regular	2	قسط 2	198788.00	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
244	77	previous_debt	0	قسط رصيد سابقة مرحّل	34795.00	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
245	77	regular	1	قسط 1	99942.75	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
246	77	regular	2	قسط 2	99942.75	2026-11-15	t	99942.75	2026-08-24 22:59:44.680752	\N
247	77	regular	3	قسط 3	99942.75	2027-01-15	t	99942.75	2026-08-24 22:59:44.680752	\N
248	77	regular	4	قسط 4	99942.75	2027-03-15	f	0.00	2026-08-24 22:59:44.680752	\N
249	78	regular	1	قسط 1	131399.00	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
250	78	regular	2	قسط 2	131399.00	2026-11-15	t	131399.00	2026-08-24 22:59:44.680752	\N
251	78	regular	3	قسط 3	131399.00	2027-01-15	t	131399.00	2026-08-24 22:59:44.680752	\N
252	79	regular	1	قسط 1	98947.25	2026-09-15	f	0.00	2026-08-24 22:59:44.680752	\N
253	79	regular	2	قسط 2	98947.25	2026-11-15	f	0.00	2026-08-24 22:59:44.680752	\N
254	79	regular	3	قسط 3	98947.25	2027-01-15	t	98947.25	2026-08-24 22:59:44.680752	\N
255	79	regular	4	قسط 4	98947.25	2027-03-15	t	98947.25	2026-08-24 22:59:44.680752	\N
256	80	regular	1	قسط 1	132801.00	2026-09-15	t	132801.00	2026-08-24 22:59:44.680752	\N
257	80	regular	2	قسط 2	132801.00	2026-11-15	t	132801.00	2026-08-24 22:59:44.680752	\N
258	80	regular	3	قسط 3	132801.00	2027-01-15	t	132801.00	2026-08-24 22:59:44.680752	\N
274	4	regular	1	قسط 1	30160.00	2026-10-01	f	30143.00	2026-09-01 04:35:22.991787	2026-09-02 03:32:33.215659
275	3	regular	1	قسط 1	6087.00	2026-10-02	f	0.00	2026-09-02 06:07:02.640626	\N
276	3	regular	2	قسط 2	6087.00	2026-11-02	f	0.00	2026-09-02 06:07:02.640626	\N
277	3	regular	3	قسط 3	6087.00	2026-12-02	f	0.00	2026-09-02 06:07:02.640626	\N
\.


--
-- Data for Name: fee_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fee_types (id, fee_name, created_at, updated_at) FROM stdin;
1	رسوم دراسية	2026-08-21 02:18:55.776515	\N
2	رسوم تسجيل	2026-08-21 02:18:55.776515	\N
3	زي مدرسي	2026-08-21 02:18:55.776515	\N
4	كتب	2026-08-21 02:18:55.776515	\N
5	مواصلات	2026-08-21 02:18:55.776515	\N
6	أنشطة	2026-08-21 02:18:55.776515	\N
\.


--
-- Data for Name: final_exam_schedules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.final_exam_schedules (id, academic_year_id, term, grade_id, subject_id, exam_date, day_name, start_time, end_time, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: grade_fee_structures; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.grade_fee_structures (id, academic_year_id, grade_id, fee_type_id, amount, created_at, updated_at) FROM stdin;
3	1	1	3	15972.00	2026-08-24 22:59:44.680752	\N
4	1	1	4	20462.00	2026-08-24 22:59:44.680752	\N
5	1	1	5	53828.00	2026-08-24 22:59:44.680752	\N
6	1	1	6	14808.00	2026-08-24 22:59:44.680752	\N
7	1	2	1	282701.00	2026-08-24 22:59:44.680752	\N
8	1	2	2	13223.00	2026-08-24 22:59:44.680752	\N
9	1	2	3	15040.00	2026-08-24 22:59:44.680752	\N
10	1	2	4	27987.00	2026-08-24 22:59:44.680752	\N
11	1	2	5	56147.00	2026-08-24 22:59:44.680752	\N
12	1	2	6	12118.00	2026-08-24 22:59:44.680752	\N
13	1	3	1	127965.00	2026-08-24 22:59:44.680752	\N
14	1	3	2	26832.00	2026-08-24 22:59:44.680752	\N
15	1	3	3	16704.00	2026-08-24 22:59:44.680752	\N
16	1	3	4	28375.00	2026-08-24 22:59:44.680752	\N
17	1	3	5	30857.00	2026-08-24 22:59:44.680752	\N
18	1	3	6	10413.00	2026-08-24 22:59:44.680752	\N
19	1	4	1	256097.00	2026-08-24 22:59:44.680752	\N
20	1	4	2	22347.00	2026-08-24 22:59:44.680752	\N
21	1	4	3	17761.00	2026-08-24 22:59:44.680752	\N
22	1	4	4	27191.00	2026-08-24 22:59:44.680752	\N
23	1	4	5	59048.00	2026-08-24 22:59:44.680752	\N
24	1	4	6	13650.00	2026-08-24 22:59:44.680752	\N
25	1	5	1	136702.00	2026-08-24 22:59:44.680752	\N
26	1	5	2	27914.00	2026-08-24 22:59:44.680752	\N
27	1	5	3	18916.00	2026-08-24 22:59:44.680752	\N
28	1	5	4	21972.00	2026-08-24 22:59:44.680752	\N
29	1	5	5	56394.00	2026-08-24 22:59:44.680752	\N
30	1	5	6	13687.00	2026-08-24 22:59:44.680752	\N
31	1	6	1	228470.00	2026-08-24 22:59:44.680752	\N
32	1	6	2	11280.00	2026-08-24 22:59:44.680752	\N
33	1	6	3	18529.00	2026-08-24 22:59:44.680752	\N
34	1	6	4	24891.00	2026-08-24 22:59:44.680752	\N
35	1	6	5	54477.00	2026-08-24 22:59:44.680752	\N
36	1	6	6	7580.00	2026-08-24 22:59:44.680752	\N
37	1	7	1	230165.00	2026-08-24 22:59:44.680752	\N
38	1	7	2	11168.00	2026-08-24 22:59:44.680752	\N
39	1	7	3	24684.00	2026-08-24 22:59:44.680752	\N
40	1	7	4	37361.00	2026-08-24 22:59:44.680752	\N
41	1	7	5	38559.00	2026-08-24 22:59:44.680752	\N
42	1	7	6	9333.00	2026-08-24 22:59:44.680752	\N
43	1	8	1	256417.00	2026-08-24 22:59:44.680752	\N
44	1	8	2	22407.00	2026-08-24 22:59:44.680752	\N
45	1	8	3	16841.00	2026-08-24 22:59:44.680752	\N
46	1	8	4	39328.00	2026-08-24 22:59:44.680752	\N
47	1	8	5	55965.00	2026-08-24 22:59:44.680752	\N
48	1	8	6	13327.00	2026-08-24 22:59:44.680752	\N
50	1	9	2	26719.00	2026-08-24 22:59:44.680752	\N
51	1	9	3	15794.00	2026-08-24 22:59:44.680752	\N
52	1	9	4	32776.00	2026-08-24 22:59:44.680752	\N
53	1	9	5	50482.00	2026-08-24 22:59:44.680752	\N
54	1	9	6	5473.00	2026-08-24 22:59:44.680752	\N
55	1	10	1	202319.00	2026-08-24 22:59:44.680752	\N
56	1	10	2	13765.00	2026-08-24 22:59:44.680752	\N
57	1	10	3	18329.00	2026-08-24 22:59:44.680752	\N
58	1	10	4	22255.00	2026-08-24 22:59:44.680752	\N
59	1	10	5	46722.00	2026-08-24 22:59:44.680752	\N
60	1	10	6	10588.00	2026-08-24 22:59:44.680752	\N
61	1	11	1	184907.00	2026-08-24 22:59:44.680752	\N
62	1	11	2	11291.00	2026-08-24 22:59:44.680752	\N
63	1	11	3	22995.00	2026-08-24 22:59:44.680752	\N
64	1	11	4	30677.00	2026-08-24 22:59:44.680752	\N
65	1	11	5	52137.00	2026-08-24 22:59:44.680752	\N
66	1	11	6	10225.00	2026-08-24 22:59:44.680752	\N
67	1	12	1	228663.00	2026-08-24 22:59:44.680752	\N
68	1	12	2	29262.00	2026-08-24 22:59:44.680752	\N
69	1	12	3	15181.00	2026-08-24 22:59:44.680752	\N
70	1	12	4	26818.00	2026-08-24 22:59:44.680752	\N
71	1	12	5	47004.00	2026-08-24 22:59:44.680752	\N
72	1	12	6	7863.00	2026-08-24 22:59:44.680752	\N
49	1	9	1	100.00	2026-08-24 22:59:44.680752	2026-08-30 14:26:16.069108
2	1	1	2	14808.00	2026-08-24 22:59:44.680752	2026-09-04 07:09:38.011076
\.


--
-- Data for Name: grades; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.grades (id, grade_name, stage_name, max_capacity, created_at, updated_at) FROM stdin;
1	الأول الأساسي	الابتدائي	30	2026-08-21 02:18:55.683456	\N
2	الثاني الأساسي	الابتدائي	30	2026-08-21 02:18:55.683456	\N
3	الثالث الأساسي	الابتدائي	30	2026-08-21 02:18:55.683456	\N
4	الرابع الأساسي	الابتدائي	30	2026-08-21 02:18:55.683456	\N
5	الخامس الأساسي	الابتدائي	30	2026-08-21 02:18:55.683456	\N
6	السادس الأساسي	الابتدائي	30	2026-08-21 02:18:55.683456	\N
7	السابع الأساسي	الإعدادي	35	2026-08-21 02:18:55.683456	\N
8	الثامن الأساسي	الإعدادي	35	2026-08-21 02:18:55.683456	\N
9	التاسع الأساسي	الإعدادي	35	2026-08-21 02:18:55.683456	\N
10	الأول الثانوي	الثانوي	40	2026-08-21 02:18:55.683456	\N
11	الثاني الثانوي	الثانوي	40	2026-08-21 02:18:55.683456	\N
12	الثالث الثانوي	الثانوي	40	2026-08-21 02:18:55.683456	\N
\.


--
-- Data for Name: homeworks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.homeworks (id, academic_year_id, grade_id, section_id, subject_id, homework_date, title, description, due_date, created_at, updated_at) FROM stdin;
1	1	1	1	1	2026-08-12	حل مسائل العلوم	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-27	2026-08-24 22:59:44.680752	\N
2	1	1	1	2	2026-08-14	كتابة مقال	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-25	2026-08-24 22:59:44.680752	\N
3	1	1	1	3	2026-08-21	حفظ سورة	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-30	2026-08-24 22:59:44.680752	\N
5	1	1	2	2	2026-08-19	مراجعة القواعد	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-26	2026-08-24 22:59:44.680752	\N
6	1	1	2	3	2026-08-18	حفظ سورة	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-26	2026-08-24 22:59:44.680752	\N
7	1	2	4	1	2026-08-15	حفظ سورة	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-31	2026-08-24 22:59:44.680752	\N
8	1	2	4	2	2026-08-19	كتابة مقال	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-29	2026-08-24 22:59:44.680752	\N
9	1	2	4	3	2026-08-11	قراءة درس اللغة العربية	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-28	2026-08-24 22:59:44.680752	\N
10	1	2	5	1	2026-08-14	مراجعة القواعد	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-27	2026-08-24 22:59:44.680752	\N
11	1	2	5	2	2026-08-14	قراءة درس اللغة العربية	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-25	2026-08-24 22:59:44.680752	\N
12	1	2	5	3	2026-08-12	حل تمارين الرياضيات	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-28	2026-08-24 22:59:44.680752	\N
13	1	3	7	1	2026-08-10	حفظ سورة	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-26	2026-08-24 22:59:44.680752	\N
14	1	3	7	2	2026-08-11	مراجعة القواعد	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-31	2026-08-24 22:59:44.680752	\N
15	1	3	7	3	2026-08-16	كتابة مقال	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-28	2026-08-24 22:59:44.680752	\N
16	1	3	8	1	2026-08-22	حل تمارين الرياضيات	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-25	2026-08-24 22:59:44.680752	\N
17	1	3	8	2	2026-08-20	حفظ سورة	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-27	2026-08-24 22:59:44.680752	\N
18	1	3	8	3	2026-08-13	مراجعة القواعد	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-27	2026-08-24 22:59:44.680752	\N
19	1	4	10	1	2026-08-11	حفظ سورة	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-29	2026-08-24 22:59:44.680752	\N
20	1	4	10	2	2026-08-13	حل تمارين الرياضيات	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-27	2026-08-24 22:59:44.680752	\N
21	1	4	10	3	2026-08-11	حفظ سورة	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-26	2026-08-24 22:59:44.680752	\N
22	1	4	11	1	2026-08-14	مراجعة القواعد	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-26	2026-08-24 22:59:44.680752	\N
23	1	4	11	2	2026-08-11	مراجعة القواعد	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-29	2026-08-24 22:59:44.680752	\N
24	1	4	11	3	2026-08-14	حل مسائل العلوم	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-31	2026-08-24 22:59:44.680752	\N
25	1	5	13	1	2026-08-16	حفظ سورة	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-31	2026-08-24 22:59:44.680752	\N
26	1	5	13	2	2026-08-15	كتابة مقال	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-25	2026-08-24 22:59:44.680752	\N
27	1	5	13	3	2026-08-12	حل تمارين الرياضيات	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-27	2026-08-24 22:59:44.680752	\N
28	1	5	14	1	2026-08-19	حل مسائل العلوم	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-25	2026-08-24 22:59:44.680752	\N
29	1	5	14	2	2026-08-16	حل مسائل العلوم	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-26	2026-08-24 22:59:44.680752	\N
30	1	5	14	3	2026-08-16	حل مسائل العلوم	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-26	2026-08-24 22:59:44.680752	\N
31	1	6	16	1	2026-08-18	كتابة مقال	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-27	2026-08-24 22:59:44.680752	\N
32	1	6	16	2	2026-08-10	كتابة مقال	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-29	2026-08-24 22:59:44.680752	\N
34	1	6	17	1	2026-08-12	مراجعة القواعد	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-28	2026-08-24 22:59:44.680752	\N
36	1	6	17	3	2026-08-16	قراءة درس اللغة العربية	يرجى حل جميع التمارين وتسليمها في الموعد المحدد	2026-08-30	2026-08-24 22:59:44.680752	\N
37	1	1	1	2	2027-08-30	ss	ss	2026-09-06	2026-08-30 17:17:55.952877	\N
\.


--
-- Data for Name: import_export_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.import_export_logs (id, operation_type, entity_name, file_name, executed_by, executed_at, status, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: monthly_evaluations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.monthly_evaluations (id, student_id, academic_year_id, grade_id, section_id, subject_id, term, month, written_score, oral_score, homework_score, attendance_score, created_at, updated_at) FROM stdin;
1	1	1	1	1	1	1	1	24.37	6.88	11.73	19.17	2026-08-24 22:59:44.680752	\N
2	1	1	1	1	1	1	2	37.80	7.22	18.40	14.72	2026-08-24 22:59:44.680752	\N
3	1	1	1	1	1	1	3	23.49	16.84	8.21	6.24	2026-08-24 22:59:44.680752	\N
4	1	1	1	1	2	1	1	36.53	13.82	8.52	19.55	2026-08-24 22:59:44.680752	\N
5	1	1	1	1	2	1	2	13.88	11.08	14.63	11.82	2026-08-24 22:59:44.680752	\N
6	1	1	1	1	2	1	3	29.49	9.82	18.23	9.77	2026-08-24 22:59:44.680752	\N
7	1	1	1	1	3	1	1	16.11	14.01	14.36	12.61	2026-08-24 22:59:44.680752	\N
8	1	1	1	1	3	1	2	18.83	9.76	5.98	16.97	2026-08-24 22:59:44.680752	\N
9	1	1	1	1	3	1	3	12.14	19.15	6.44	13.85	2026-08-24 22:59:44.680752	\N
10	1	1	1	1	4	1	1	39.87	6.80	18.59	14.15	2026-08-24 22:59:44.680752	\N
11	1	1	1	1	4	1	2	37.02	13.79	7.37	17.58	2026-08-24 22:59:44.680752	\N
12	1	1	1	1	4	1	3	25.68	17.76	10.24	5.41	2026-08-24 22:59:44.680752	\N
13	1	1	1	1	5	1	1	11.44	6.41	13.27	19.60	2026-08-24 22:59:44.680752	\N
14	1	1	1	1	5	1	2	29.87	5.61	14.64	7.14	2026-08-24 22:59:44.680752	\N
15	1	1	1	1	5	1	3	28.65	12.17	6.87	5.14	2026-08-24 22:59:44.680752	\N
16	2	1	1	1	1	1	1	35.24	13.90	7.15	15.21	2026-08-24 22:59:44.680752	\N
17	2	1	1	1	1	1	2	13.47	5.06	10.55	18.45	2026-08-24 22:59:44.680752	\N
18	2	1	1	1	1	1	3	11.54	15.00	6.67	6.56	2026-08-24 22:59:44.680752	\N
19	2	1	1	1	2	1	1	23.18	8.47	11.09	6.68	2026-08-24 22:59:44.680752	\N
20	2	1	1	1	2	1	2	11.65	5.84	5.96	11.71	2026-08-24 22:59:44.680752	\N
21	2	1	1	1	2	1	3	32.31	8.36	17.84	15.18	2026-08-24 22:59:44.680752	\N
22	2	1	1	1	3	1	1	28.60	16.50	12.51	9.86	2026-08-24 22:59:44.680752	\N
23	2	1	1	1	3	1	2	21.71	8.38	18.06	5.53	2026-08-24 22:59:44.680752	\N
24	2	1	1	1	3	1	3	19.89	18.51	12.60	13.99	2026-08-24 22:59:44.680752	\N
25	2	1	1	1	4	1	1	29.00	11.47	5.17	13.51	2026-08-24 22:59:44.680752	\N
26	2	1	1	1	4	1	2	34.64	5.01	5.45	16.51	2026-08-24 22:59:44.680752	\N
27	2	1	1	1	4	1	3	34.20	18.64	6.17	17.72	2026-08-24 22:59:44.680752	\N
28	2	1	1	1	5	1	1	21.71	13.46	18.48	11.23	2026-08-24 22:59:44.680752	\N
29	2	1	1	1	5	1	2	28.42	7.40	14.63	14.97	2026-08-24 22:59:44.680752	\N
30	2	1	1	1	5	1	3	24.86	6.83	6.78	7.61	2026-08-24 22:59:44.680752	\N
32	3	1	1	1	1	1	2	35.55	11.18	18.65	17.71	2026-08-24 22:59:44.680752	\N
33	3	1	1	1	1	1	3	31.21	11.11	19.64	9.93	2026-08-24 22:59:44.680752	\N
34	3	1	1	1	2	1	1	19.41	14.78	11.36	19.37	2026-08-24 22:59:44.680752	\N
35	3	1	1	1	2	1	2	25.36	14.53	16.91	8.76	2026-08-24 22:59:44.680752	\N
36	3	1	1	1	2	1	3	28.29	12.42	19.42	9.89	2026-08-24 22:59:44.680752	\N
37	3	1	1	1	3	1	1	36.43	5.51	11.79	15.36	2026-08-24 22:59:44.680752	\N
38	3	1	1	1	3	1	2	24.15	18.94	13.17	18.70	2026-08-24 22:59:44.680752	\N
39	3	1	1	1	3	1	3	34.39	11.44	10.08	16.69	2026-08-24 22:59:44.680752	\N
40	3	1	1	1	4	1	1	23.35	18.25	5.22	5.48	2026-08-24 22:59:44.680752	\N
41	3	1	1	1	4	1	2	10.10	19.03	19.32	14.06	2026-08-24 22:59:44.680752	\N
42	3	1	1	1	4	1	3	18.67	13.38	15.90	13.92	2026-08-24 22:59:44.680752	\N
43	3	1	1	1	5	1	1	34.29	10.14	15.59	7.11	2026-08-24 22:59:44.680752	\N
44	3	1	1	1	5	1	2	34.08	5.13	13.17	17.10	2026-08-24 22:59:44.680752	\N
45	3	1	1	1	5	1	3	13.13	15.64	18.35	18.97	2026-08-24 22:59:44.680752	\N
47	4	1	1	1	1	1	2	10.03	16.67	8.39	19.29	2026-08-24 22:59:44.680752	\N
48	4	1	1	1	1	1	3	28.17	12.35	12.51	7.16	2026-08-24 22:59:44.680752	\N
49	4	1	1	1	2	1	1	14.47	16.70	18.94	6.74	2026-08-24 22:59:44.680752	\N
50	4	1	1	1	2	1	2	14.44	12.27	5.87	14.69	2026-08-24 22:59:44.680752	\N
51	4	1	1	1	2	1	3	38.93	5.98	7.78	11.72	2026-08-24 22:59:44.680752	\N
52	4	1	1	1	3	1	1	14.49	15.69	12.69	12.18	2026-08-24 22:59:44.680752	\N
53	4	1	1	1	3	1	2	31.48	8.60	7.24	15.43	2026-08-24 22:59:44.680752	\N
54	4	1	1	1	3	1	3	24.44	18.11	16.89	19.11	2026-08-24 22:59:44.680752	\N
55	4	1	1	1	4	1	1	16.83	12.61	19.98	15.51	2026-08-24 22:59:44.680752	\N
56	4	1	1	1	4	1	2	21.41	7.52	10.24	12.04	2026-08-24 22:59:44.680752	\N
57	4	1	1	1	4	1	3	20.64	16.12	8.10	10.80	2026-08-24 22:59:44.680752	\N
58	4	1	1	1	5	1	1	31.37	9.22	9.05	14.84	2026-08-24 22:59:44.680752	\N
59	4	1	1	1	5	1	2	30.95	13.31	19.62	13.77	2026-08-24 22:59:44.680752	\N
60	4	1	1	1	5	1	3	22.40	13.62	14.38	9.13	2026-08-24 22:59:44.680752	\N
62	5	1	1	1	1	1	2	16.66	15.68	5.81	14.72	2026-08-24 22:59:44.680752	\N
63	5	1	1	1	1	1	3	39.28	7.36	17.84	11.83	2026-08-24 22:59:44.680752	\N
64	5	1	1	1	2	1	1	32.90	16.29	15.99	7.33	2026-08-24 22:59:44.680752	\N
65	5	1	1	1	2	1	2	19.82	17.57	15.32	14.87	2026-08-24 22:59:44.680752	\N
66	5	1	1	1	2	1	3	17.66	17.41	10.90	16.25	2026-08-24 22:59:44.680752	\N
67	5	1	1	1	3	1	1	37.02	15.64	17.14	13.29	2026-08-24 22:59:44.680752	\N
68	5	1	1	1	3	1	2	39.10	12.18	8.52	17.11	2026-08-24 22:59:44.680752	\N
69	5	1	1	1	3	1	3	15.67	6.65	11.31	12.85	2026-08-24 22:59:44.680752	\N
70	5	1	1	1	4	1	1	37.15	5.77	19.24	19.79	2026-08-24 22:59:44.680752	\N
71	5	1	1	1	4	1	2	22.47	16.15	5.03	7.32	2026-08-24 22:59:44.680752	\N
72	5	1	1	1	4	1	3	12.62	18.54	13.42	15.68	2026-08-24 22:59:44.680752	\N
73	5	1	1	1	5	1	1	13.72	19.70	14.70	17.58	2026-08-24 22:59:44.680752	\N
74	5	1	1	1	5	1	2	37.17	8.38	18.82	5.66	2026-08-24 22:59:44.680752	\N
75	5	1	1	1	5	1	3	14.68	6.03	8.64	19.01	2026-08-24 22:59:44.680752	\N
77	6	1	1	1	1	1	2	10.62	18.44	7.82	12.10	2026-08-24 22:59:44.680752	\N
78	6	1	1	1	1	1	3	24.67	17.73	13.37	9.04	2026-08-24 22:59:44.680752	\N
79	6	1	1	1	2	1	1	29.37	15.15	9.21	11.51	2026-08-24 22:59:44.680752	\N
80	6	1	1	1	2	1	2	15.97	10.17	12.84	11.23	2026-08-24 22:59:44.680752	\N
81	6	1	1	1	2	1	3	22.55	18.78	8.65	13.69	2026-08-24 22:59:44.680752	\N
82	6	1	1	1	3	1	1	13.31	16.00	16.66	7.21	2026-08-24 22:59:44.680752	\N
83	6	1	1	1	3	1	2	35.02	11.09	11.67	8.10	2026-08-24 22:59:44.680752	\N
84	6	1	1	1	3	1	3	28.47	14.02	13.89	9.33	2026-08-24 22:59:44.680752	\N
85	6	1	1	1	4	1	1	29.57	11.36	19.14	10.72	2026-08-24 22:59:44.680752	\N
86	6	1	1	1	4	1	2	31.94	12.69	9.43	19.59	2026-08-24 22:59:44.680752	\N
87	6	1	1	1	4	1	3	16.71	5.11	17.61	13.39	2026-08-24 22:59:44.680752	\N
88	6	1	1	1	5	1	1	27.69	8.25	11.34	7.40	2026-08-24 22:59:44.680752	\N
89	6	1	1	1	5	1	2	30.76	18.09	9.05	18.91	2026-08-24 22:59:44.680752	\N
90	6	1	1	1	5	1	3	17.36	9.56	15.20	17.19	2026-08-24 22:59:44.680752	\N
92	7	1	1	1	1	1	2	15.81	12.85	9.59	17.59	2026-08-24 22:59:44.680752	\N
93	7	1	1	1	1	1	3	28.31	14.62	14.40	14.18	2026-08-24 22:59:44.680752	\N
94	7	1	1	1	2	1	1	27.55	10.00	9.29	7.04	2026-08-24 22:59:44.680752	\N
95	7	1	1	1	2	1	2	33.51	12.13	7.25	7.97	2026-08-24 22:59:44.680752	\N
96	7	1	1	1	2	1	3	21.98	15.58	11.81	14.29	2026-08-24 22:59:44.680752	\N
97	7	1	1	1	3	1	1	29.53	8.99	18.06	9.75	2026-08-24 22:59:44.680752	\N
98	7	1	1	1	3	1	2	34.13	16.55	19.61	5.77	2026-08-24 22:59:44.680752	\N
99	7	1	1	1	3	1	3	25.58	17.23	7.08	16.65	2026-08-24 22:59:44.680752	\N
100	7	1	1	1	4	1	1	37.67	5.82	13.76	7.65	2026-08-24 22:59:44.680752	\N
101	7	1	1	1	4	1	2	21.66	16.79	17.58	13.59	2026-08-24 22:59:44.680752	\N
102	7	1	1	1	4	1	3	35.13	10.47	14.22	10.31	2026-08-24 22:59:44.680752	\N
103	7	1	1	1	5	1	1	34.35	18.83	17.35	7.16	2026-08-24 22:59:44.680752	\N
104	7	1	1	1	5	1	2	32.86	19.57	8.82	19.13	2026-08-24 22:59:44.680752	\N
105	7	1	1	1	5	1	3	16.16	16.97	13.26	15.98	2026-08-24 22:59:44.680752	\N
107	8	1	1	1	1	1	2	32.14	14.90	16.01	16.41	2026-08-24 22:59:44.680752	\N
108	8	1	1	1	1	1	3	22.61	13.92	11.51	18.30	2026-08-24 22:59:44.680752	\N
109	8	1	1	1	2	1	1	12.08	16.45	7.43	14.47	2026-08-24 22:59:44.680752	\N
110	8	1	1	1	2	1	2	26.36	14.30	6.57	14.69	2026-08-24 22:59:44.680752	\N
111	8	1	1	1	2	1	3	20.41	13.60	10.82	10.48	2026-08-24 22:59:44.680752	\N
112	8	1	1	1	3	1	1	18.17	8.19	10.48	5.21	2026-08-24 22:59:44.680752	\N
113	8	1	1	1	3	1	2	28.34	19.38	10.52	15.30	2026-08-24 22:59:44.680752	\N
114	8	1	1	1	3	1	3	11.12	13.25	19.60	13.08	2026-08-24 22:59:44.680752	\N
115	8	1	1	1	4	1	1	36.39	7.85	15.80	18.72	2026-08-24 22:59:44.680752	\N
116	8	1	1	1	4	1	2	34.71	13.42	15.92	13.93	2026-08-24 22:59:44.680752	\N
117	8	1	1	1	4	1	3	33.00	14.24	7.10	13.62	2026-08-24 22:59:44.680752	\N
118	8	1	1	1	5	1	1	26.86	8.84	18.94	14.91	2026-08-24 22:59:44.680752	\N
119	8	1	1	1	5	1	2	35.29	14.54	8.54	6.76	2026-08-24 22:59:44.680752	\N
120	8	1	1	1	5	1	3	22.90	6.61	15.67	8.53	2026-08-24 22:59:44.680752	\N
121	9	1	1	1	1	1	1	16.33	11.60	18.47	7.03	2026-08-24 22:59:44.680752	\N
122	9	1	1	1	1	1	2	14.49	11.81	11.29	16.90	2026-08-24 22:59:44.680752	\N
123	9	1	1	1	1	1	3	11.06	10.56	5.44	15.52	2026-08-24 22:59:44.680752	\N
124	9	1	1	1	2	1	1	38.26	16.74	9.79	18.17	2026-08-24 22:59:44.680752	\N
125	9	1	1	1	2	1	2	13.41	11.15	6.51	5.17	2026-08-24 22:59:44.680752	\N
126	9	1	1	1	2	1	3	18.07	11.96	17.24	14.90	2026-08-24 22:59:44.680752	\N
127	9	1	1	1	3	1	1	13.01	16.83	9.52	15.46	2026-08-24 22:59:44.680752	\N
128	9	1	1	1	3	1	2	27.43	10.00	18.55	5.84	2026-08-24 22:59:44.680752	\N
129	9	1	1	1	3	1	3	31.88	7.71	11.29	13.66	2026-08-24 22:59:44.680752	\N
130	9	1	1	1	4	1	1	25.03	9.80	14.94	9.99	2026-08-24 22:59:44.680752	\N
131	9	1	1	1	4	1	2	18.80	16.01	6.99	8.19	2026-08-24 22:59:44.680752	\N
132	9	1	1	1	4	1	3	10.87	8.86	12.28	16.76	2026-08-24 22:59:44.680752	\N
133	9	1	1	1	5	1	1	22.78	15.31	6.68	18.07	2026-08-24 22:59:44.680752	\N
134	9	1	1	1	5	1	2	33.69	13.97	13.37	10.67	2026-08-24 22:59:44.680752	\N
135	9	1	1	1	5	1	3	28.94	13.74	13.93	16.30	2026-08-24 22:59:44.680752	\N
137	10	1	1	1	1	1	2	13.23	8.98	19.65	15.87	2026-08-24 22:59:44.680752	\N
138	10	1	1	1	1	1	3	39.66	19.35	10.49	14.11	2026-08-24 22:59:44.680752	\N
139	10	1	1	1	2	1	1	15.42	17.93	17.85	6.94	2026-08-24 22:59:44.680752	\N
140	10	1	1	1	2	1	2	23.56	5.09	16.86	19.41	2026-08-24 22:59:44.680752	\N
141	10	1	1	1	2	1	3	35.62	9.96	15.35	10.45	2026-08-24 22:59:44.680752	\N
142	10	1	1	1	3	1	1	31.21	15.44	17.16	17.81	2026-08-24 22:59:44.680752	\N
143	10	1	1	1	3	1	2	38.40	14.09	12.77	10.04	2026-08-24 22:59:44.680752	\N
144	10	1	1	1	3	1	3	29.21	8.54	14.42	11.17	2026-08-24 22:59:44.680752	\N
145	10	1	1	1	4	1	1	10.84	15.04	14.53	9.81	2026-08-24 22:59:44.680752	\N
146	10	1	1	1	4	1	2	10.90	5.15	12.70	6.64	2026-08-24 22:59:44.680752	\N
147	10	1	1	1	4	1	3	21.75	15.21	19.92	17.92	2026-08-24 22:59:44.680752	\N
148	10	1	1	1	5	1	1	13.29	18.92	7.98	13.78	2026-08-24 22:59:44.680752	\N
149	10	1	1	1	5	1	2	12.11	17.62	6.40	11.53	2026-08-24 22:59:44.680752	\N
150	10	1	1	1	5	1	3	28.81	15.69	12.69	11.28	2026-08-24 22:59:44.680752	\N
152	11	1	1	1	1	1	2	36.74	8.75	14.34	19.31	2026-08-24 22:59:44.680752	\N
153	11	1	1	1	1	1	3	25.07	9.47	11.78	10.54	2026-08-24 22:59:44.680752	\N
154	11	1	1	1	2	1	1	33.61	10.83	9.28	5.09	2026-08-24 22:59:44.680752	\N
155	11	1	1	1	2	1	2	20.46	12.58	9.55	10.63	2026-08-24 22:59:44.680752	\N
156	11	1	1	1	2	1	3	25.67	13.54	13.05	10.74	2026-08-24 22:59:44.680752	\N
157	11	1	1	1	3	1	1	20.47	13.79	14.37	8.10	2026-08-24 22:59:44.680752	\N
158	11	1	1	1	3	1	2	29.29	7.18	5.79	14.88	2026-08-24 22:59:44.680752	\N
159	11	1	1	1	3	1	3	38.11	7.85	13.92	9.94	2026-08-24 22:59:44.680752	\N
160	11	1	1	1	4	1	1	24.27	5.97	12.08	19.95	2026-08-24 22:59:44.680752	\N
161	11	1	1	1	4	1	2	37.95	17.61	9.94	7.26	2026-08-24 22:59:44.680752	\N
162	11	1	1	1	4	1	3	24.16	8.48	7.39	6.47	2026-08-24 22:59:44.680752	\N
163	11	1	1	1	5	1	1	22.62	11.66	16.95	11.09	2026-08-24 22:59:44.680752	\N
164	11	1	1	1	5	1	2	16.43	16.46	5.91	16.55	2026-08-24 22:59:44.680752	\N
165	11	1	1	1	5	1	3	19.15	12.41	10.64	13.16	2026-08-24 22:59:44.680752	\N
167	12	1	1	1	1	1	2	33.97	13.03	7.61	16.53	2026-08-24 22:59:44.680752	\N
168	12	1	1	1	1	1	3	37.04	15.55	17.06	8.28	2026-08-24 22:59:44.680752	\N
169	12	1	1	1	2	1	1	20.69	9.73	6.21	15.57	2026-08-24 22:59:44.680752	\N
170	12	1	1	1	2	1	2	19.19	11.16	16.02	15.24	2026-08-24 22:59:44.680752	\N
171	12	1	1	1	2	1	3	19.66	5.43	18.05	5.54	2026-08-24 22:59:44.680752	\N
172	12	1	1	1	3	1	1	23.33	6.29	7.94	18.44	2026-08-24 22:59:44.680752	\N
173	12	1	1	1	3	1	2	16.39	10.63	12.57	13.04	2026-08-24 22:59:44.680752	\N
174	12	1	1	1	3	1	3	12.71	14.18	18.00	15.74	2026-08-24 22:59:44.680752	\N
175	12	1	1	1	4	1	1	17.14	17.06	6.24	7.55	2026-08-24 22:59:44.680752	\N
176	12	1	1	1	4	1	2	36.08	15.51	18.85	7.48	2026-08-24 22:59:44.680752	\N
177	12	1	1	1	4	1	3	27.38	16.60	14.65	17.77	2026-08-24 22:59:44.680752	\N
178	12	1	1	1	5	1	1	23.75	16.66	9.19	13.24	2026-08-24 22:59:44.680752	\N
179	12	1	1	1	5	1	2	35.96	17.13	12.20	9.07	2026-08-24 22:59:44.680752	\N
180	12	1	1	1	5	1	3	12.27	11.87	5.94	9.17	2026-08-24 22:59:44.680752	\N
182	13	1	1	1	1	1	2	19.60	11.90	7.00	12.98	2026-08-24 22:59:44.680752	\N
183	13	1	1	1	1	1	3	36.58	5.17	19.09	12.68	2026-08-24 22:59:44.680752	\N
184	13	1	1	1	2	1	1	21.11	11.61	8.44	17.84	2026-08-24 22:59:44.680752	\N
185	13	1	1	1	2	1	2	10.41	14.94	13.37	8.30	2026-08-24 22:59:44.680752	\N
186	13	1	1	1	2	1	3	18.00	7.92	7.10	6.76	2026-08-24 22:59:44.680752	\N
187	13	1	1	1	3	1	1	15.69	15.37	14.24	12.09	2026-08-24 22:59:44.680752	\N
188	13	1	1	1	3	1	2	12.05	19.42	5.24	10.89	2026-08-24 22:59:44.680752	\N
189	13	1	1	1	3	1	3	24.46	12.46	11.47	8.91	2026-08-24 22:59:44.680752	\N
190	13	1	1	1	4	1	1	14.57	15.02	11.32	18.85	2026-08-24 22:59:44.680752	\N
191	13	1	1	1	4	1	2	24.83	13.03	18.59	7.52	2026-08-24 22:59:44.680752	\N
192	13	1	1	1	4	1	3	12.71	7.32	8.01	8.20	2026-08-24 22:59:44.680752	\N
193	13	1	1	1	5	1	1	26.52	5.24	12.67	18.83	2026-08-24 22:59:44.680752	\N
194	13	1	1	1	5	1	2	31.46	11.48	10.93	5.01	2026-08-24 22:59:44.680752	\N
195	13	1	1	1	5	1	3	33.67	19.74	13.03	11.60	2026-08-24 22:59:44.680752	\N
197	14	1	1	1	1	1	2	17.08	18.19	12.48	17.06	2026-08-24 22:59:44.680752	\N
198	14	1	1	1	1	1	3	16.22	5.93	7.01	8.11	2026-08-24 22:59:44.680752	\N
199	14	1	1	1	2	1	1	10.66	10.95	15.26	5.41	2026-08-24 22:59:44.680752	\N
200	14	1	1	1	2	1	2	31.87	17.31	17.63	10.47	2026-08-24 22:59:44.680752	\N
201	14	1	1	1	2	1	3	14.49	14.67	15.60	9.69	2026-08-24 22:59:44.680752	\N
202	14	1	1	1	3	1	1	22.35	5.96	17.77	5.77	2026-08-24 22:59:44.680752	\N
203	14	1	1	1	3	1	2	18.94	13.09	13.06	16.17	2026-08-24 22:59:44.680752	\N
204	14	1	1	1	3	1	3	33.38	17.61	6.61	13.95	2026-08-24 22:59:44.680752	\N
205	14	1	1	1	4	1	1	12.94	9.34	12.59	11.60	2026-08-24 22:59:44.680752	\N
206	14	1	1	1	4	1	2	22.45	16.72	18.20	15.04	2026-08-24 22:59:44.680752	\N
207	14	1	1	1	4	1	3	24.42	15.97	6.62	9.79	2026-08-24 22:59:44.680752	\N
208	14	1	1	1	5	1	1	27.53	5.23	6.39	8.02	2026-08-24 22:59:44.680752	\N
209	14	1	1	1	5	1	2	39.03	11.51	17.27	14.23	2026-08-24 22:59:44.680752	\N
210	14	1	1	1	5	1	3	15.09	5.97	8.05	16.22	2026-08-24 22:59:44.680752	\N
212	15	1	1	1	1	1	2	22.32	12.91	11.95	13.26	2026-08-24 22:59:44.680752	\N
213	15	1	1	1	1	1	3	26.57	19.49	10.31	15.95	2026-08-24 22:59:44.680752	\N
214	15	1	1	1	2	1	1	18.63	8.43	9.10	14.77	2026-08-24 22:59:44.680752	\N
215	15	1	1	1	2	1	2	19.46	6.60	11.12	5.42	2026-08-24 22:59:44.680752	\N
216	15	1	1	1	2	1	3	19.42	7.36	17.67	5.48	2026-08-24 22:59:44.680752	\N
217	15	1	1	1	3	1	1	19.64	17.02	15.61	5.95	2026-08-24 22:59:44.680752	\N
218	15	1	1	1	3	1	2	34.95	15.33	12.07	18.90	2026-08-24 22:59:44.680752	\N
219	15	1	1	1	3	1	3	13.09	8.57	19.77	18.28	2026-08-24 22:59:44.680752	\N
220	15	1	1	1	4	1	1	30.84	7.57	17.55	9.90	2026-08-24 22:59:44.680752	\N
221	15	1	1	1	4	1	2	25.79	11.21	13.50	10.69	2026-08-24 22:59:44.680752	\N
222	15	1	1	1	4	1	3	35.66	10.53	8.73	19.48	2026-08-24 22:59:44.680752	\N
223	15	1	1	1	5	1	1	25.51	9.91	5.96	16.80	2026-08-24 22:59:44.680752	\N
224	15	1	1	1	5	1	2	12.14	15.40	13.91	8.43	2026-08-24 22:59:44.680752	\N
225	15	1	1	1	5	1	3	37.28	13.72	7.43	9.91	2026-08-24 22:59:44.680752	\N
227	16	1	1	1	1	1	2	29.30	10.94	18.04	16.97	2026-08-24 22:59:44.680752	\N
228	16	1	1	1	1	1	3	12.15	19.83	8.63	10.18	2026-08-24 22:59:44.680752	\N
229	16	1	1	1	2	1	1	36.51	16.95	14.01	11.71	2026-08-24 22:59:44.680752	\N
230	16	1	1	1	2	1	2	29.62	13.67	19.23	6.72	2026-08-24 22:59:44.680752	\N
231	16	1	1	1	2	1	3	35.17	9.96	9.70	12.66	2026-08-24 22:59:44.680752	\N
232	16	1	1	1	3	1	1	10.91	12.98	9.72	18.32	2026-08-24 22:59:44.680752	\N
233	16	1	1	1	3	1	2	25.70	19.73	15.63	15.64	2026-08-24 22:59:44.680752	\N
234	16	1	1	1	3	1	3	28.49	13.32	18.19	7.51	2026-08-24 22:59:44.680752	\N
235	16	1	1	1	4	1	1	36.21	5.96	10.00	6.07	2026-08-24 22:59:44.680752	\N
236	16	1	1	1	4	1	2	16.12	6.18	18.87	9.70	2026-08-24 22:59:44.680752	\N
237	16	1	1	1	4	1	3	33.55	9.77	14.99	13.11	2026-08-24 22:59:44.680752	\N
238	16	1	1	1	5	1	1	38.99	12.67	13.38	15.04	2026-08-24 22:59:44.680752	\N
239	16	1	1	1	5	1	2	32.03	16.97	5.15	15.70	2026-08-24 22:59:44.680752	\N
240	16	1	1	1	5	1	3	19.17	8.13	9.28	13.11	2026-08-24 22:59:44.680752	\N
242	17	1	1	1	1	1	2	25.61	11.76	13.70	5.33	2026-08-24 22:59:44.680752	\N
243	17	1	1	1	1	1	3	33.30	6.61	15.80	14.24	2026-08-24 22:59:44.680752	\N
244	17	1	1	1	2	1	1	22.98	18.29	14.93	7.14	2026-08-24 22:59:44.680752	\N
245	17	1	1	1	2	1	2	14.32	9.72	13.56	10.77	2026-08-24 22:59:44.680752	\N
246	17	1	1	1	2	1	3	34.94	14.61	19.52	8.54	2026-08-24 22:59:44.680752	\N
247	17	1	1	1	3	1	1	26.17	16.50	16.16	10.87	2026-08-24 22:59:44.680752	\N
248	17	1	1	1	3	1	2	30.36	18.51	6.39	8.36	2026-08-24 22:59:44.680752	\N
249	17	1	1	1	3	1	3	24.24	8.57	15.27	8.93	2026-08-24 22:59:44.680752	\N
250	17	1	1	1	4	1	1	39.41	17.81	7.91	13.90	2026-08-24 22:59:44.680752	\N
251	17	1	1	1	4	1	2	34.85	18.35	11.52	16.40	2026-08-24 22:59:44.680752	\N
252	17	1	1	1	4	1	3	20.76	8.55	6.36	16.69	2026-08-24 22:59:44.680752	\N
253	17	1	1	1	5	1	1	17.34	13.65	11.82	6.24	2026-08-24 22:59:44.680752	\N
254	17	1	1	1	5	1	2	17.30	7.54	5.55	11.50	2026-08-24 22:59:44.680752	\N
255	17	1	1	1	5	1	3	36.91	16.84	8.01	13.54	2026-08-24 22:59:44.680752	\N
257	18	1	1	1	1	1	2	23.44	17.33	8.67	5.57	2026-08-24 22:59:44.680752	\N
258	18	1	1	1	1	1	3	16.91	14.20	10.12	18.95	2026-08-24 22:59:44.680752	\N
259	18	1	1	1	2	1	1	27.88	13.83	12.93	16.85	2026-08-24 22:59:44.680752	\N
260	18	1	1	1	2	1	2	22.71	9.85	19.04	12.09	2026-08-24 22:59:44.680752	\N
261	18	1	1	1	2	1	3	19.81	12.98	11.55	7.51	2026-08-24 22:59:44.680752	\N
262	18	1	1	1	3	1	1	16.20	17.80	19.76	18.01	2026-08-24 22:59:44.680752	\N
263	18	1	1	1	3	1	2	15.43	6.70	10.08	14.68	2026-08-24 22:59:44.680752	\N
264	18	1	1	1	3	1	3	10.14	8.94	16.06	13.93	2026-08-24 22:59:44.680752	\N
265	18	1	1	1	4	1	1	37.15	5.41	15.08	8.02	2026-08-24 22:59:44.680752	\N
266	18	1	1	1	4	1	2	17.38	14.41	13.72	6.41	2026-08-24 22:59:44.680752	\N
267	18	1	1	1	4	1	3	18.77	15.85	7.17	18.67	2026-08-24 22:59:44.680752	\N
268	18	1	1	1	5	1	1	37.04	16.90	6.95	12.81	2026-08-24 22:59:44.680752	\N
269	18	1	1	1	5	1	2	21.29	11.27	11.78	12.63	2026-08-24 22:59:44.680752	\N
270	18	1	1	1	5	1	3	15.62	17.05	13.40	14.00	2026-08-24 22:59:44.680752	\N
271	19	1	1	1	1	1	1	26.24	17.52	13.86	14.32	2026-08-24 22:59:44.680752	\N
272	19	1	1	1	1	1	2	22.22	8.68	17.08	19.74	2026-08-24 22:59:44.680752	\N
273	19	1	1	1	1	1	3	34.92	16.92	13.11	15.01	2026-08-24 22:59:44.680752	\N
274	19	1	1	1	2	1	1	22.96	14.57	18.84	6.06	2026-08-24 22:59:44.680752	\N
275	19	1	1	1	2	1	2	29.76	14.20	17.05	18.63	2026-08-24 22:59:44.680752	\N
276	19	1	1	1	2	1	3	20.65	14.04	7.17	16.44	2026-08-24 22:59:44.680752	\N
277	19	1	1	1	3	1	1	16.04	12.84	13.64	18.65	2026-08-24 22:59:44.680752	\N
278	19	1	1	1	3	1	2	11.34	13.47	14.62	14.90	2026-08-24 22:59:44.680752	\N
279	19	1	1	1	3	1	3	34.22	9.11	11.75	19.29	2026-08-24 22:59:44.680752	\N
280	19	1	1	1	4	1	1	29.79	8.62	16.74	6.43	2026-08-24 22:59:44.680752	\N
281	19	1	1	1	4	1	2	29.49	5.20	16.16	11.72	2026-08-24 22:59:44.680752	\N
282	19	1	1	1	4	1	3	33.95	9.80	12.14	19.81	2026-08-24 22:59:44.680752	\N
283	19	1	1	1	5	1	1	22.76	19.09	18.55	18.87	2026-08-24 22:59:44.680752	\N
284	19	1	1	1	5	1	2	27.46	5.62	15.23	6.30	2026-08-24 22:59:44.680752	\N
285	19	1	1	1	5	1	3	20.10	10.74	11.89	15.63	2026-08-24 22:59:44.680752	\N
286	20	1	1	2	1	1	1	34.48	19.77	6.28	17.03	2026-08-24 22:59:44.680752	\N
287	20	1	1	2	1	1	2	39.13	8.47	15.38	5.08	2026-08-24 22:59:44.680752	\N
288	20	1	1	2	1	1	3	25.54	13.08	12.17	5.46	2026-08-24 22:59:44.680752	\N
289	20	1	1	2	2	1	1	15.45	5.28	16.71	11.65	2026-08-24 22:59:44.680752	\N
290	20	1	1	2	2	1	2	35.37	13.03	11.70	8.22	2026-08-24 22:59:44.680752	\N
291	20	1	1	2	2	1	3	15.82	10.38	10.03	10.87	2026-08-24 22:59:44.680752	\N
292	20	1	1	2	3	1	1	24.40	11.09	17.94	5.44	2026-08-24 22:59:44.680752	\N
293	20	1	1	2	3	1	2	38.21	18.16	13.46	10.52	2026-08-24 22:59:44.680752	\N
294	20	1	1	2	3	1	3	31.11	8.69	14.22	5.55	2026-08-24 22:59:44.680752	\N
295	20	1	1	2	4	1	1	16.24	13.94	11.29	18.39	2026-08-24 22:59:44.680752	\N
296	20	1	1	2	4	1	2	15.00	6.76	14.22	8.63	2026-08-24 22:59:44.680752	\N
297	20	1	1	2	4	1	3	25.42	14.09	7.69	8.94	2026-08-24 22:59:44.680752	\N
298	20	1	1	2	5	1	1	22.95	12.93	15.45	18.27	2026-08-24 22:59:44.680752	\N
299	20	1	1	2	5	1	2	15.40	11.26	14.68	10.08	2026-08-24 22:59:44.680752	\N
300	20	1	1	2	5	1	3	22.72	5.76	9.23	5.99	2026-08-24 22:59:44.680752	\N
301	21	1	1	2	1	1	1	36.09	12.67	10.68	16.65	2026-08-24 22:59:44.680752	\N
302	21	1	1	2	1	1	2	38.43	14.98	5.80	17.49	2026-08-24 22:59:44.680752	\N
303	21	1	1	2	1	1	3	14.47	14.30	17.65	9.16	2026-08-24 22:59:44.680752	\N
304	21	1	1	2	2	1	1	25.19	10.71	9.45	16.57	2026-08-24 22:59:44.680752	\N
305	21	1	1	2	2	1	2	10.76	6.86	17.36	10.34	2026-08-24 22:59:44.680752	\N
306	21	1	1	2	2	1	3	37.54	15.66	9.70	13.12	2026-08-24 22:59:44.680752	\N
307	21	1	1	2	3	1	1	23.12	13.57	17.26	15.34	2026-08-24 22:59:44.680752	\N
308	21	1	1	2	3	1	2	31.23	15.32	9.21	6.55	2026-08-24 22:59:44.680752	\N
309	21	1	1	2	3	1	3	38.19	10.18	16.42	14.42	2026-08-24 22:59:44.680752	\N
310	21	1	1	2	4	1	1	25.19	11.14	16.26	7.50	2026-08-24 22:59:44.680752	\N
311	21	1	1	2	4	1	2	14.74	13.77	14.91	12.60	2026-08-24 22:59:44.680752	\N
312	21	1	1	2	4	1	3	33.32	10.05	9.46	6.75	2026-08-24 22:59:44.680752	\N
313	21	1	1	2	5	1	1	18.46	16.86	10.71	17.15	2026-08-24 22:59:44.680752	\N
314	21	1	1	2	5	1	2	21.39	15.09	6.62	16.66	2026-08-24 22:59:44.680752	\N
315	21	1	1	2	5	1	3	17.91	18.32	12.36	8.54	2026-08-24 22:59:44.680752	\N
316	22	1	1	2	1	1	1	14.80	10.23	12.58	10.22	2026-08-24 22:59:44.680752	\N
317	22	1	1	2	1	1	2	39.15	8.26	16.70	17.40	2026-08-24 22:59:44.680752	\N
318	22	1	1	2	1	1	3	18.89	11.68	7.00	10.58	2026-08-24 22:59:44.680752	\N
319	22	1	1	2	2	1	1	36.50	6.68	18.55	17.68	2026-08-24 22:59:44.680752	\N
320	22	1	1	2	2	1	2	14.14	19.30	8.30	7.21	2026-08-24 22:59:44.680752	\N
321	22	1	1	2	2	1	3	15.07	19.12	13.38	12.62	2026-08-24 22:59:44.680752	\N
322	22	1	1	2	3	1	1	39.89	6.80	12.35	19.72	2026-08-24 22:59:44.680752	\N
323	22	1	1	2	3	1	2	18.03	6.57	6.06	18.50	2026-08-24 22:59:44.680752	\N
324	22	1	1	2	3	1	3	19.72	11.63	11.83	5.86	2026-08-24 22:59:44.680752	\N
325	22	1	1	2	4	1	1	13.75	9.71	8.95	5.40	2026-08-24 22:59:44.680752	\N
326	22	1	1	2	4	1	2	15.35	8.97	11.68	9.68	2026-08-24 22:59:44.680752	\N
327	22	1	1	2	4	1	3	20.86	9.66	6.03	11.12	2026-08-24 22:59:44.680752	\N
328	22	1	1	2	5	1	1	29.69	11.47	17.73	5.20	2026-08-24 22:59:44.680752	\N
329	22	1	1	2	5	1	2	16.95	5.56	8.77	9.35	2026-08-24 22:59:44.680752	\N
330	22	1	1	2	5	1	3	24.94	7.63	5.16	8.51	2026-08-24 22:59:44.680752	\N
331	23	1	1	2	1	1	1	35.66	18.25	9.79	16.54	2026-08-24 22:59:44.680752	\N
332	23	1	1	2	1	1	2	18.95	15.61	17.93	18.72	2026-08-24 22:59:44.680752	\N
333	23	1	1	2	1	1	3	13.19	15.73	16.69	9.99	2026-08-24 22:59:44.680752	\N
334	23	1	1	2	2	1	1	18.09	17.67	5.40	15.44	2026-08-24 22:59:44.680752	\N
335	23	1	1	2	2	1	2	24.56	12.55	13.64	8.21	2026-08-24 22:59:44.680752	\N
336	23	1	1	2	2	1	3	33.58	13.49	18.33	17.55	2026-08-24 22:59:44.680752	\N
337	23	1	1	2	3	1	1	17.95	14.29	18.78	19.42	2026-08-24 22:59:44.680752	\N
338	23	1	1	2	3	1	2	26.00	19.72	7.09	18.32	2026-08-24 22:59:44.680752	\N
339	23	1	1	2	3	1	3	29.39	15.90	9.60	19.69	2026-08-24 22:59:44.680752	\N
340	23	1	1	2	4	1	1	26.51	7.52	16.11	18.81	2026-08-24 22:59:44.680752	\N
341	23	1	1	2	4	1	2	18.65	5.95	10.73	15.97	2026-08-24 22:59:44.680752	\N
342	23	1	1	2	4	1	3	13.28	7.29	18.11	18.66	2026-08-24 22:59:44.680752	\N
343	23	1	1	2	5	1	1	19.15	18.63	10.19	6.61	2026-08-24 22:59:44.680752	\N
344	23	1	1	2	5	1	2	33.53	5.48	14.20	19.98	2026-08-24 22:59:44.680752	\N
345	23	1	1	2	5	1	3	16.48	17.20	9.10	11.19	2026-08-24 22:59:44.680752	\N
346	24	1	1	2	1	1	1	14.70	7.79	15.15	15.13	2026-08-24 22:59:44.680752	\N
347	24	1	1	2	1	1	2	19.42	16.93	5.42	18.53	2026-08-24 22:59:44.680752	\N
348	24	1	1	2	1	1	3	21.58	13.75	18.44	8.51	2026-08-24 22:59:44.680752	\N
349	24	1	1	2	2	1	1	29.55	7.18	10.19	17.10	2026-08-24 22:59:44.680752	\N
350	24	1	1	2	2	1	2	26.49	10.97	18.91	17.55	2026-08-24 22:59:44.680752	\N
351	24	1	1	2	2	1	3	32.52	18.55	10.12	15.79	2026-08-24 22:59:44.680752	\N
352	24	1	1	2	3	1	1	19.22	11.26	14.03	10.63	2026-08-24 22:59:44.680752	\N
353	24	1	1	2	3	1	2	21.35	15.48	19.29	19.37	2026-08-24 22:59:44.680752	\N
354	24	1	1	2	3	1	3	26.53	16.61	8.59	7.16	2026-08-24 22:59:44.680752	\N
355	24	1	1	2	4	1	1	19.67	12.95	14.99	5.02	2026-08-24 22:59:44.680752	\N
356	24	1	1	2	4	1	2	39.12	8.15	17.87	7.48	2026-08-24 22:59:44.680752	\N
357	24	1	1	2	4	1	3	31.77	12.62	10.17	11.79	2026-08-24 22:59:44.680752	\N
358	24	1	1	2	5	1	1	21.01	12.54	15.08	6.77	2026-08-24 22:59:44.680752	\N
359	24	1	1	2	5	1	2	16.62	8.37	11.16	18.57	2026-08-24 22:59:44.680752	\N
360	24	1	1	2	5	1	3	27.49	16.60	19.39	13.53	2026-08-24 22:59:44.680752	\N
361	25	1	1	2	1	1	1	36.82	11.62	13.34	13.32	2026-08-24 22:59:44.680752	\N
362	25	1	1	2	1	1	2	38.11	15.37	15.80	18.58	2026-08-24 22:59:44.680752	\N
363	25	1	1	2	1	1	3	12.38	18.37	7.84	10.94	2026-08-24 22:59:44.680752	\N
364	25	1	1	2	2	1	1	18.82	6.35	19.13	19.22	2026-08-24 22:59:44.680752	\N
365	25	1	1	2	2	1	2	30.59	11.66	19.67	16.02	2026-08-24 22:59:44.680752	\N
366	25	1	1	2	2	1	3	38.67	17.05	11.19	18.19	2026-08-24 22:59:44.680752	\N
367	25	1	1	2	3	1	1	11.06	12.43	13.32	18.15	2026-08-24 22:59:44.680752	\N
368	25	1	1	2	3	1	2	16.11	18.09	10.11	7.37	2026-08-24 22:59:44.680752	\N
369	25	1	1	2	3	1	3	13.83	16.95	10.85	16.09	2026-08-24 22:59:44.680752	\N
370	25	1	1	2	4	1	1	20.59	7.58	17.58	18.48	2026-08-24 22:59:44.680752	\N
371	25	1	1	2	4	1	2	28.47	18.65	7.93	11.71	2026-08-24 22:59:44.680752	\N
372	25	1	1	2	4	1	3	38.99	17.82	17.47	5.64	2026-08-24 22:59:44.680752	\N
373	25	1	1	2	5	1	1	22.07	18.37	5.29	9.44	2026-08-24 22:59:44.680752	\N
374	25	1	1	2	5	1	2	20.30	11.43	17.28	12.68	2026-08-24 22:59:44.680752	\N
375	25	1	1	2	5	1	3	25.45	9.50	8.05	9.42	2026-08-24 22:59:44.680752	\N
376	26	1	1	2	1	1	1	19.33	10.90	6.21	5.01	2026-08-24 22:59:44.680752	\N
377	26	1	1	2	1	1	2	10.48	13.38	18.35	19.62	2026-08-24 22:59:44.680752	\N
378	26	1	1	2	1	1	3	27.57	15.69	5.78	14.12	2026-08-24 22:59:44.680752	\N
379	26	1	1	2	2	1	1	22.33	19.62	10.06	18.60	2026-08-24 22:59:44.680752	\N
380	26	1	1	2	2	1	2	23.95	10.85	11.20	5.15	2026-08-24 22:59:44.680752	\N
381	26	1	1	2	2	1	3	35.90	19.68	13.92	14.79	2026-08-24 22:59:44.680752	\N
382	26	1	1	2	3	1	1	18.39	6.58	11.12	15.03	2026-08-24 22:59:44.680752	\N
383	26	1	1	2	3	1	2	17.23	8.92	13.48	14.58	2026-08-24 22:59:44.680752	\N
384	26	1	1	2	3	1	3	13.03	19.00	12.18	15.29	2026-08-24 22:59:44.680752	\N
385	26	1	1	2	4	1	1	12.81	11.27	13.42	6.81	2026-08-24 22:59:44.680752	\N
386	26	1	1	2	4	1	2	15.32	13.80	6.49	13.67	2026-08-24 22:59:44.680752	\N
387	26	1	1	2	4	1	3	11.80	17.75	19.61	10.58	2026-08-24 22:59:44.680752	\N
388	26	1	1	2	5	1	1	19.50	5.41	14.43	8.33	2026-08-24 22:59:44.680752	\N
389	26	1	1	2	5	1	2	16.36	6.67	8.25	5.61	2026-08-24 22:59:44.680752	\N
390	26	1	1	2	5	1	3	19.15	19.50	8.20	16.80	2026-08-24 22:59:44.680752	\N
391	27	1	1	2	1	1	1	10.15	9.17	5.94	6.98	2026-08-24 22:59:44.680752	\N
392	27	1	1	2	1	1	2	11.73	11.13	16.40	14.81	2026-08-24 22:59:44.680752	\N
393	27	1	1	2	1	1	3	31.18	5.11	9.13	19.92	2026-08-24 22:59:44.680752	\N
394	27	1	1	2	2	1	1	30.40	12.50	5.11	17.21	2026-08-24 22:59:44.680752	\N
395	27	1	1	2	2	1	2	17.27	8.84	5.85	19.23	2026-08-24 22:59:44.680752	\N
396	27	1	1	2	2	1	3	37.19	19.86	18.85	18.89	2026-08-24 22:59:44.680752	\N
397	27	1	1	2	3	1	1	28.23	14.03	9.61	11.90	2026-08-24 22:59:44.680752	\N
398	27	1	1	2	3	1	2	15.09	15.54	8.90	16.76	2026-08-24 22:59:44.680752	\N
399	27	1	1	2	3	1	3	38.98	6.45	10.50	9.00	2026-08-24 22:59:44.680752	\N
400	27	1	1	2	4	1	1	12.14	8.93	15.57	16.69	2026-08-24 22:59:44.680752	\N
401	27	1	1	2	4	1	2	36.50	8.85	19.88	6.39	2026-08-24 22:59:44.680752	\N
402	27	1	1	2	4	1	3	32.43	15.01	13.77	10.48	2026-08-24 22:59:44.680752	\N
403	27	1	1	2	5	1	1	12.47	8.89	12.74	18.93	2026-08-24 22:59:44.680752	\N
404	27	1	1	2	5	1	2	32.19	6.46	12.36	19.36	2026-08-24 22:59:44.680752	\N
405	27	1	1	2	5	1	3	17.78	17.41	19.85	11.95	2026-08-24 22:59:44.680752	\N
406	28	1	1	2	1	1	1	15.66	15.94	14.12	6.41	2026-08-24 22:59:44.680752	\N
407	28	1	1	2	1	1	2	10.93	14.87	7.73	5.42	2026-08-24 22:59:44.680752	\N
408	28	1	1	2	1	1	3	16.32	6.37	8.39	9.10	2026-08-24 22:59:44.680752	\N
409	28	1	1	2	2	1	1	12.85	11.96	18.87	11.05	2026-08-24 22:59:44.680752	\N
410	28	1	1	2	2	1	2	12.32	8.90	8.95	17.48	2026-08-24 22:59:44.680752	\N
411	28	1	1	2	2	1	3	13.58	16.83	6.68	8.80	2026-08-24 22:59:44.680752	\N
412	28	1	1	2	3	1	1	28.45	8.20	17.37	12.08	2026-08-24 22:59:44.680752	\N
413	28	1	1	2	3	1	2	29.24	8.65	9.08	6.19	2026-08-24 22:59:44.680752	\N
414	28	1	1	2	3	1	3	12.97	15.16	8.02	11.97	2026-08-24 22:59:44.680752	\N
415	28	1	1	2	4	1	1	12.86	5.95	8.22	14.22	2026-08-24 22:59:44.680752	\N
416	28	1	1	2	4	1	2	24.78	8.49	10.60	11.54	2026-08-24 22:59:44.680752	\N
417	28	1	1	2	4	1	3	17.91	14.92	17.07	8.22	2026-08-24 22:59:44.680752	\N
418	28	1	1	2	5	1	1	33.67	11.06	6.00	7.84	2026-08-24 22:59:44.680752	\N
419	28	1	1	2	5	1	2	33.00	10.01	14.71	16.88	2026-08-24 22:59:44.680752	\N
420	28	1	1	2	5	1	3	12.87	10.23	10.93	12.89	2026-08-24 22:59:44.680752	\N
421	29	1	1	2	1	1	1	34.91	16.25	11.10	19.58	2026-08-24 22:59:44.680752	\N
422	29	1	1	2	1	1	2	22.75	6.79	11.33	17.87	2026-08-24 22:59:44.680752	\N
423	29	1	1	2	1	1	3	34.65	7.50	6.89	11.38	2026-08-24 22:59:44.680752	\N
424	29	1	1	2	2	1	1	27.65	13.55	17.33	10.56	2026-08-24 22:59:44.680752	\N
425	29	1	1	2	2	1	2	39.10	9.87	5.50	11.95	2026-08-24 22:59:44.680752	\N
426	29	1	1	2	2	1	3	38.94	5.80	12.22	19.51	2026-08-24 22:59:44.680752	\N
427	29	1	1	2	3	1	1	16.91	16.15	13.69	19.60	2026-08-24 22:59:44.680752	\N
428	29	1	1	2	3	1	2	33.41	17.78	14.27	18.41	2026-08-24 22:59:44.680752	\N
429	29	1	1	2	3	1	3	26.10	19.14	6.12	16.64	2026-08-24 22:59:44.680752	\N
430	29	1	1	2	4	1	1	15.24	11.40	11.50	7.37	2026-08-24 22:59:44.680752	\N
431	29	1	1	2	4	1	2	16.53	18.37	8.55	15.87	2026-08-24 22:59:44.680752	\N
432	29	1	1	2	4	1	3	33.73	14.55	7.12	6.29	2026-08-24 22:59:44.680752	\N
433	29	1	1	2	5	1	1	37.61	5.45	10.69	15.39	2026-08-24 22:59:44.680752	\N
434	29	1	1	2	5	1	2	25.77	9.16	15.85	17.83	2026-08-24 22:59:44.680752	\N
435	29	1	1	2	5	1	3	18.40	9.73	10.14	12.02	2026-08-24 22:59:44.680752	\N
436	30	1	1	2	1	1	1	32.77	10.46	9.12	17.13	2026-08-24 22:59:44.680752	\N
437	30	1	1	2	1	1	2	13.95	8.93	5.95	9.41	2026-08-24 22:59:44.680752	\N
438	30	1	1	2	1	1	3	13.00	10.85	9.65	15.10	2026-08-24 22:59:44.680752	\N
439	30	1	1	2	2	1	1	26.47	8.88	12.04	10.58	2026-08-24 22:59:44.680752	\N
440	30	1	1	2	2	1	2	13.58	17.04	7.76	6.49	2026-08-24 22:59:44.680752	\N
441	30	1	1	2	2	1	3	10.76	6.89	11.21	18.85	2026-08-24 22:59:44.680752	\N
442	30	1	1	2	3	1	1	34.30	18.74	8.23	8.98	2026-08-24 22:59:44.680752	\N
443	30	1	1	2	3	1	2	32.07	14.33	12.37	10.62	2026-08-24 22:59:44.680752	\N
444	30	1	1	2	3	1	3	30.91	5.69	7.36	19.18	2026-08-24 22:59:44.680752	\N
445	30	1	1	2	4	1	1	20.49	11.66	7.22	16.76	2026-08-24 22:59:44.680752	\N
446	30	1	1	2	4	1	2	16.37	12.35	8.41	10.68	2026-08-24 22:59:44.680752	\N
447	30	1	1	2	4	1	3	38.15	12.91	10.30	11.49	2026-08-24 22:59:44.680752	\N
448	30	1	1	2	5	1	1	13.96	5.72	6.29	14.28	2026-08-24 22:59:44.680752	\N
449	30	1	1	2	5	1	2	34.11	19.47	18.48	19.61	2026-08-24 22:59:44.680752	\N
450	30	1	1	2	5	1	3	13.18	13.41	14.45	19.64	2026-08-24 22:59:44.680752	\N
451	31	1	1	2	1	1	1	33.95	15.19	14.46	9.63	2026-08-24 22:59:44.680752	\N
452	31	1	1	2	1	1	2	34.23	5.38	9.81	7.85	2026-08-24 22:59:44.680752	\N
453	31	1	1	2	1	1	3	13.31	14.24	15.69	17.37	2026-08-24 22:59:44.680752	\N
454	31	1	1	2	2	1	1	26.88	12.14	9.33	16.86	2026-08-24 22:59:44.680752	\N
455	31	1	1	2	2	1	2	31.10	10.96	6.88	12.64	2026-08-24 22:59:44.680752	\N
456	31	1	1	2	2	1	3	33.46	11.29	6.19	5.23	2026-08-24 22:59:44.680752	\N
457	31	1	1	2	3	1	1	15.45	16.68	14.76	19.63	2026-08-24 22:59:44.680752	\N
458	31	1	1	2	3	1	2	35.20	9.22	6.04	5.32	2026-08-24 22:59:44.680752	\N
459	31	1	1	2	3	1	3	39.31	6.84	7.49	11.34	2026-08-24 22:59:44.680752	\N
460	31	1	1	2	4	1	1	35.63	6.33	11.80	7.39	2026-08-24 22:59:44.680752	\N
461	31	1	1	2	4	1	2	30.60	12.26	6.73	16.01	2026-08-24 22:59:44.680752	\N
462	31	1	1	2	4	1	3	35.58	18.00	13.84	5.18	2026-08-24 22:59:44.680752	\N
463	31	1	1	2	5	1	1	39.32	5.02	16.83	13.38	2026-08-24 22:59:44.680752	\N
464	31	1	1	2	5	1	2	22.00	11.77	11.35	17.99	2026-08-24 22:59:44.680752	\N
465	31	1	1	2	5	1	3	19.81	19.76	13.49	19.34	2026-08-24 22:59:44.680752	\N
466	32	1	1	2	1	1	1	37.11	6.50	5.13	5.19	2026-08-24 22:59:44.680752	\N
467	32	1	1	2	1	1	2	10.35	18.22	14.04	19.19	2026-08-24 22:59:44.680752	\N
468	32	1	1	2	1	1	3	13.76	15.56	9.40	8.77	2026-08-24 22:59:44.680752	\N
469	32	1	1	2	2	1	1	16.51	17.67	8.80	17.02	2026-08-24 22:59:44.680752	\N
470	32	1	1	2	2	1	2	21.83	15.07	7.12	9.02	2026-08-24 22:59:44.680752	\N
471	32	1	1	2	2	1	3	39.67	6.04	19.68	19.01	2026-08-24 22:59:44.680752	\N
472	32	1	1	2	3	1	1	35.29	16.36	5.61	17.26	2026-08-24 22:59:44.680752	\N
473	32	1	1	2	3	1	2	30.34	14.27	19.93	18.45	2026-08-24 22:59:44.680752	\N
474	32	1	1	2	3	1	3	11.94	16.94	5.77	13.21	2026-08-24 22:59:44.680752	\N
475	32	1	1	2	4	1	1	18.18	11.56	17.50	9.86	2026-08-24 22:59:44.680752	\N
476	32	1	1	2	4	1	2	16.28	7.01	6.75	12.76	2026-08-24 22:59:44.680752	\N
477	32	1	1	2	4	1	3	32.72	17.28	7.15	14.41	2026-08-24 22:59:44.680752	\N
478	32	1	1	2	5	1	1	26.65	14.03	16.58	11.99	2026-08-24 22:59:44.680752	\N
479	32	1	1	2	5	1	2	20.12	18.41	13.16	17.57	2026-08-24 22:59:44.680752	\N
480	32	1	1	2	5	1	3	33.60	5.40	7.25	12.45	2026-08-24 22:59:44.680752	\N
481	33	1	1	2	1	1	1	33.51	7.06	14.88	15.29	2026-08-24 22:59:44.680752	\N
482	33	1	1	2	1	1	2	27.04	13.41	15.87	11.00	2026-08-24 22:59:44.680752	\N
483	33	1	1	2	1	1	3	38.51	10.80	7.42	18.71	2026-08-24 22:59:44.680752	\N
484	33	1	1	2	2	1	1	25.95	8.27	16.68	11.20	2026-08-24 22:59:44.680752	\N
485	33	1	1	2	2	1	2	25.73	7.79	14.49	7.90	2026-08-24 22:59:44.680752	\N
486	33	1	1	2	2	1	3	18.77	5.07	12.71	6.25	2026-08-24 22:59:44.680752	\N
487	33	1	1	2	3	1	1	13.34	19.54	9.12	17.91	2026-08-24 22:59:44.680752	\N
488	33	1	1	2	3	1	2	28.65	7.66	16.36	8.37	2026-08-24 22:59:44.680752	\N
489	33	1	1	2	3	1	3	11.84	8.64	19.21	7.08	2026-08-24 22:59:44.680752	\N
490	33	1	1	2	4	1	1	10.11	8.33	9.48	11.58	2026-08-24 22:59:44.680752	\N
491	33	1	1	2	4	1	2	14.11	10.42	13.40	19.74	2026-08-24 22:59:44.680752	\N
492	33	1	1	2	4	1	3	23.11	13.92	6.56	18.25	2026-08-24 22:59:44.680752	\N
493	33	1	1	2	5	1	1	29.72	12.73	14.02	15.58	2026-08-24 22:59:44.680752	\N
494	33	1	1	2	5	1	2	18.11	6.48	12.89	19.53	2026-08-24 22:59:44.680752	\N
495	33	1	1	2	5	1	3	19.33	19.29	16.73	19.64	2026-08-24 22:59:44.680752	\N
496	34	1	1	2	1	1	1	19.94	17.37	13.66	19.97	2026-08-24 22:59:44.680752	\N
497	34	1	1	2	1	1	2	36.83	10.24	15.73	18.04	2026-08-24 22:59:44.680752	\N
498	34	1	1	2	1	1	3	33.92	7.63	19.58	12.20	2026-08-24 22:59:44.680752	\N
499	34	1	1	2	2	1	1	23.66	18.31	5.37	10.91	2026-08-24 22:59:44.680752	\N
500	34	1	1	2	2	1	2	12.00	7.91	15.33	18.62	2026-08-24 22:59:44.680752	\N
501	34	1	1	2	2	1	3	22.89	15.37	16.95	12.65	2026-08-24 22:59:44.680752	\N
502	34	1	1	2	3	1	1	36.22	6.69	9.40	16.71	2026-08-24 22:59:44.680752	\N
503	34	1	1	2	3	1	2	25.45	10.15	19.53	16.09	2026-08-24 22:59:44.680752	\N
504	34	1	1	2	3	1	3	38.73	15.37	11.31	13.99	2026-08-24 22:59:44.680752	\N
505	34	1	1	2	4	1	1	17.57	16.63	9.19	15.26	2026-08-24 22:59:44.680752	\N
506	34	1	1	2	4	1	2	35.34	14.31	7.77	18.58	2026-08-24 22:59:44.680752	\N
507	34	1	1	2	4	1	3	23.96	16.49	6.04	11.64	2026-08-24 22:59:44.680752	\N
508	34	1	1	2	5	1	1	18.31	10.98	8.10	6.81	2026-08-24 22:59:44.680752	\N
509	34	1	1	2	5	1	2	39.33	13.08	18.10	7.94	2026-08-24 22:59:44.680752	\N
510	34	1	1	2	5	1	3	10.70	11.56	11.30	18.77	2026-08-24 22:59:44.680752	\N
511	35	1	1	3	1	1	1	38.02	15.58	11.46	9.72	2026-08-24 22:59:44.680752	\N
512	35	1	1	3	1	1	2	26.47	5.46	5.31	17.13	2026-08-24 22:59:44.680752	\N
513	35	1	1	3	1	1	3	34.45	8.95	13.18	16.26	2026-08-24 22:59:44.680752	\N
514	35	1	1	3	2	1	1	22.41	19.20	18.41	11.28	2026-08-24 22:59:44.680752	\N
515	35	1	1	3	2	1	2	30.34	8.54	12.76	14.08	2026-08-24 22:59:44.680752	\N
516	35	1	1	3	2	1	3	33.03	18.92	9.16	15.70	2026-08-24 22:59:44.680752	\N
517	35	1	1	3	3	1	1	32.38	13.83	15.85	16.07	2026-08-24 22:59:44.680752	\N
518	35	1	1	3	3	1	2	17.52	6.04	5.88	5.38	2026-08-24 22:59:44.680752	\N
519	35	1	1	3	3	1	3	17.69	19.97	19.86	16.12	2026-08-24 22:59:44.680752	\N
520	35	1	1	3	4	1	1	19.32	15.72	9.87	9.54	2026-08-24 22:59:44.680752	\N
521	35	1	1	3	4	1	2	23.62	16.07	18.74	14.02	2026-08-24 22:59:44.680752	\N
522	35	1	1	3	4	1	3	23.25	12.81	13.22	12.58	2026-08-24 22:59:44.680752	\N
523	35	1	1	3	5	1	1	20.89	18.12	5.07	12.88	2026-08-24 22:59:44.680752	\N
524	35	1	1	3	5	1	2	27.93	15.62	15.04	15.75	2026-08-24 22:59:44.680752	\N
525	35	1	1	3	5	1	3	38.20	5.77	19.10	14.82	2026-08-24 22:59:44.680752	\N
526	36	1	1	3	1	1	1	21.75	17.13	8.90	12.18	2026-08-24 22:59:44.680752	\N
527	36	1	1	3	1	1	2	14.58	18.01	18.89	17.11	2026-08-24 22:59:44.680752	\N
528	36	1	1	3	1	1	3	26.63	8.55	5.66	12.40	2026-08-24 22:59:44.680752	\N
529	36	1	1	3	2	1	1	31.22	7.95	12.91	7.31	2026-08-24 22:59:44.680752	\N
530	36	1	1	3	2	1	2	16.61	12.42	19.42	8.19	2026-08-24 22:59:44.680752	\N
531	36	1	1	3	2	1	3	17.41	15.92	5.14	8.47	2026-08-24 22:59:44.680752	\N
532	36	1	1	3	3	1	1	22.96	14.49	5.24	9.77	2026-08-24 22:59:44.680752	\N
533	36	1	1	3	3	1	2	26.72	11.82	19.07	17.36	2026-08-24 22:59:44.680752	\N
534	36	1	1	3	3	1	3	28.95	19.41	11.23	7.06	2026-08-24 22:59:44.680752	\N
535	36	1	1	3	4	1	1	38.59	10.06	11.17	14.31	2026-08-24 22:59:44.680752	\N
536	36	1	1	3	4	1	2	11.38	14.33	16.88	8.58	2026-08-24 22:59:44.680752	\N
537	36	1	1	3	4	1	3	34.55	18.47	10.45	13.14	2026-08-24 22:59:44.680752	\N
538	36	1	1	3	5	1	1	18.03	14.05	9.94	18.70	2026-08-24 22:59:44.680752	\N
539	36	1	1	3	5	1	2	37.84	12.87	17.72	9.94	2026-08-24 22:59:44.680752	\N
540	36	1	1	3	5	1	3	21.97	17.27	10.48	14.53	2026-08-24 22:59:44.680752	\N
541	37	1	1	3	1	1	1	16.47	7.98	18.81	5.40	2026-08-24 22:59:44.680752	\N
542	37	1	1	3	1	1	2	11.51	13.83	17.95	6.30	2026-08-24 22:59:44.680752	\N
543	37	1	1	3	1	1	3	15.53	12.71	6.23	18.54	2026-08-24 22:59:44.680752	\N
544	37	1	1	3	2	1	1	26.85	5.61	12.00	5.16	2026-08-24 22:59:44.680752	\N
545	37	1	1	3	2	1	2	19.96	12.48	17.10	6.28	2026-08-24 22:59:44.680752	\N
546	37	1	1	3	2	1	3	14.86	6.80	13.38	8.51	2026-08-24 22:59:44.680752	\N
547	37	1	1	3	3	1	1	29.50	5.78	15.86	9.68	2026-08-24 22:59:44.680752	\N
548	37	1	1	3	3	1	2	18.18	15.75	8.49	17.83	2026-08-24 22:59:44.680752	\N
549	37	1	1	3	3	1	3	16.46	14.61	12.48	8.67	2026-08-24 22:59:44.680752	\N
550	37	1	1	3	4	1	1	23.37	6.90	6.55	15.53	2026-08-24 22:59:44.680752	\N
551	37	1	1	3	4	1	2	39.07	5.39	9.68	13.79	2026-08-24 22:59:44.680752	\N
552	37	1	1	3	4	1	3	30.12	9.97	12.22	7.52	2026-08-24 22:59:44.680752	\N
553	37	1	1	3	5	1	1	38.50	16.31	15.21	12.95	2026-08-24 22:59:44.680752	\N
554	37	1	1	3	5	1	2	13.16	12.22	16.81	14.98	2026-08-24 22:59:44.680752	\N
555	37	1	1	3	5	1	3	20.02	13.00	6.54	18.02	2026-08-24 22:59:44.680752	\N
556	38	1	1	3	1	1	1	17.57	7.66	8.06	12.82	2026-08-24 22:59:44.680752	\N
557	38	1	1	3	1	1	2	35.93	14.46	6.64	19.49	2026-08-24 22:59:44.680752	\N
558	38	1	1	3	1	1	3	31.30	7.35	16.47	6.33	2026-08-24 22:59:44.680752	\N
559	38	1	1	3	2	1	1	34.33	7.18	7.05	12.43	2026-08-24 22:59:44.680752	\N
560	38	1	1	3	2	1	2	15.56	13.18	18.37	6.54	2026-08-24 22:59:44.680752	\N
561	38	1	1	3	2	1	3	17.50	19.87	12.41	17.65	2026-08-24 22:59:44.680752	\N
562	38	1	1	3	3	1	1	12.93	9.04	7.68	7.55	2026-08-24 22:59:44.680752	\N
563	38	1	1	3	3	1	2	31.50	13.70	9.99	5.93	2026-08-24 22:59:44.680752	\N
564	38	1	1	3	3	1	3	36.28	11.78	8.26	5.35	2026-08-24 22:59:44.680752	\N
565	38	1	1	3	4	1	1	13.14	8.03	12.11	7.79	2026-08-24 22:59:44.680752	\N
566	38	1	1	3	4	1	2	39.62	7.11	13.68	18.67	2026-08-24 22:59:44.680752	\N
567	38	1	1	3	4	1	3	20.10	18.05	14.39	13.73	2026-08-24 22:59:44.680752	\N
568	38	1	1	3	5	1	1	37.96	18.75	9.55	6.98	2026-08-24 22:59:44.680752	\N
569	38	1	1	3	5	1	2	13.27	5.66	7.48	16.14	2026-08-24 22:59:44.680752	\N
570	38	1	1	3	5	1	3	22.41	19.35	5.49	19.88	2026-08-24 22:59:44.680752	\N
571	39	1	1	3	1	1	1	21.64	6.77	12.01	10.65	2026-08-24 22:59:44.680752	\N
572	39	1	1	3	1	1	2	23.73	11.58	9.89	18.70	2026-08-24 22:59:44.680752	\N
573	39	1	1	3	1	1	3	19.01	15.24	17.17	13.41	2026-08-24 22:59:44.680752	\N
574	39	1	1	3	2	1	1	36.85	15.80	11.29	19.76	2026-08-24 22:59:44.680752	\N
575	39	1	1	3	2	1	2	18.56	17.36	15.28	15.79	2026-08-24 22:59:44.680752	\N
576	39	1	1	3	2	1	3	18.99	9.39	16.07	7.66	2026-08-24 22:59:44.680752	\N
577	39	1	1	3	3	1	1	28.75	14.48	6.67	6.57	2026-08-24 22:59:44.680752	\N
578	39	1	1	3	3	1	2	37.63	10.34	5.04	17.35	2026-08-24 22:59:44.680752	\N
579	39	1	1	3	3	1	3	14.84	16.54	6.35	8.09	2026-08-24 22:59:44.680752	\N
580	39	1	1	3	4	1	1	31.13	18.79	5.29	9.65	2026-08-24 22:59:44.680752	\N
581	39	1	1	3	4	1	2	18.24	12.74	5.17	6.93	2026-08-24 22:59:44.680752	\N
582	39	1	1	3	4	1	3	25.41	17.76	9.17	8.24	2026-08-24 22:59:44.680752	\N
583	39	1	1	3	5	1	1	12.70	11.08	12.23	6.10	2026-08-24 22:59:44.680752	\N
584	39	1	1	3	5	1	2	29.26	19.00	16.25	6.48	2026-08-24 22:59:44.680752	\N
585	39	1	1	3	5	1	3	11.34	14.61	18.47	16.93	2026-08-24 22:59:44.680752	\N
586	40	1	1	3	1	1	1	29.28	14.24	7.09	11.34	2026-08-24 22:59:44.680752	\N
587	40	1	1	3	1	1	2	14.34	14.57	7.11	19.37	2026-08-24 22:59:44.680752	\N
588	40	1	1	3	1	1	3	13.17	15.93	15.24	5.06	2026-08-24 22:59:44.680752	\N
589	40	1	1	3	2	1	1	10.26	15.33	19.13	6.07	2026-08-24 22:59:44.680752	\N
590	40	1	1	3	2	1	2	36.11	19.50	9.00	9.55	2026-08-24 22:59:44.680752	\N
591	40	1	1	3	2	1	3	25.45	9.99	8.32	18.83	2026-08-24 22:59:44.680752	\N
592	40	1	1	3	3	1	1	35.15	7.08	16.33	18.26	2026-08-24 22:59:44.680752	\N
593	40	1	1	3	3	1	2	34.81	11.00	18.50	14.33	2026-08-24 22:59:44.680752	\N
594	40	1	1	3	3	1	3	34.63	8.29	18.01	18.98	2026-08-24 22:59:44.680752	\N
595	40	1	1	3	4	1	1	13.94	9.06	16.53	7.04	2026-08-24 22:59:44.680752	\N
596	40	1	1	3	4	1	2	34.79	13.26	12.31	17.20	2026-08-24 22:59:44.680752	\N
597	40	1	1	3	4	1	3	19.61	15.98	8.70	17.15	2026-08-24 22:59:44.680752	\N
598	40	1	1	3	5	1	1	10.59	17.47	12.65	18.89	2026-08-24 22:59:44.680752	\N
599	40	1	1	3	5	1	2	19.79	11.44	17.53	13.22	2026-08-24 22:59:44.680752	\N
600	40	1	1	3	5	1	3	32.37	5.71	12.26	5.22	2026-08-24 22:59:44.680752	\N
31	3	1	1	1	1	1	1	0.00	0.00	0.00	0.00	2026-08-24 22:59:44.680752	2026-08-25 05:13:07.616395
46	4	1	1	1	1	1	1	0.00	0.00	0.00	0.00	2026-08-24 22:59:44.680752	2026-08-25 05:13:07.616395
61	5	1	1	1	1	1	1	0.00	0.00	0.00	0.00	2026-08-24 22:59:44.680752	2026-08-25 05:13:07.616395
106	8	1	1	1	1	1	1	0.00	0.00	0.00	0.00	2026-08-24 22:59:44.680752	2026-08-25 05:13:07.616395
136	10	1	1	1	1	1	1	0.00	0.00	0.00	0.00	2026-08-24 22:59:44.680752	2026-08-25 05:13:07.616395
151	11	1	1	1	1	1	1	0.00	0.00	0.00	0.00	2026-08-24 22:59:44.680752	2026-08-25 05:13:07.616395
181	13	1	1	1	1	1	1	0.00	0.00	0.00	0.00	2026-08-24 22:59:44.680752	2026-08-25 05:13:07.616395
211	15	1	1	1	1	1	1	0.00	0.00	0.00	0.00	2026-08-24 22:59:44.680752	2026-08-25 05:13:07.616395
226	16	1	1	1	1	1	1	0.00	0.00	0.00	0.00	2026-08-24 22:59:44.680752	2026-08-25 05:13:07.616395
241	17	1	1	1	1	1	1	0.00	0.00	0.00	0.00	2026-08-24 22:59:44.680752	2026-08-25 05:13:07.616395
166	12	1	1	1	1	1	1	0.00	0.00	0.00	0.00	2026-08-24 22:59:44.680752	2026-08-25 05:39:37.204374
601	693	1	1	1	1	1	1	5.50	5.50	5.00	7.00	2026-08-25 05:13:07.616395	2026-08-25 05:39:37.204374
76	6	1	1	1	1	1	1	0.00	20.00	0.00	0.00	2026-08-24 22:59:44.680752	2026-08-30 16:56:39.578797
91	7	1	1	1	1	1	1	0.00	3.00	0.00	0.00	2026-08-24 22:59:44.680752	2026-08-30 16:56:39.578797
196	14	1	1	1	1	1	1	0.00	20.00	0.00	0.00	2026-08-24 22:59:44.680752	2026-08-30 16:56:39.578797
602	66	1	2	4	1	1	1	30.00	4.00	10.00	20.00	2026-08-30 16:58:27.165997	\N
603	71	1	2	4	1	1	1	0.00	0.00	0.00	0.00	2026-08-30 16:58:27.165997	\N
604	69	1	2	4	1	1	1	0.00	0.00	0.00	0.00	2026-08-30 16:58:27.165997	\N
605	52	1	2	4	1	1	1	0.00	0.00	0.00	0.00	2026-08-30 16:58:27.165997	\N
606	60	1	2	4	1	1	1	0.00	0.00	0.00	0.00	2026-08-30 16:58:27.165997	\N
607	56	1	2	4	1	1	1	0.00	0.00	0.00	0.00	2026-08-30 16:58:27.165997	\N
608	65	1	2	4	1	1	1	0.00	0.00	0.00	0.00	2026-08-30 16:58:27.165997	\N
609	63	1	2	4	1	1	1	0.00	0.00	0.00	0.00	2026-08-30 16:58:27.165997	\N
610	57	1	2	4	1	1	1	0.00	0.00	0.00	0.00	2026-08-30 16:58:27.165997	\N
611	72	1	2	4	1	1	1	0.00	0.00	0.00	0.00	2026-08-30 16:58:27.165997	\N
612	55	1	2	4	1	1	1	0.00	0.00	0.00	0.00	2026-08-30 16:58:27.165997	\N
613	64	1	2	4	1	1	1	0.00	0.00	0.00	0.00	2026-08-30 16:58:27.165997	\N
614	53	1	2	4	1	1	1	0.00	0.00	0.00	0.00	2026-08-30 16:58:27.165997	\N
615	51	1	2	4	1	1	1	0.00	0.00	0.00	0.00	2026-08-30 16:58:27.165997	\N
616	61	1	2	4	1	1	1	0.00	0.00	0.00	0.00	2026-08-30 16:58:27.165997	\N
617	54	1	2	4	1	1	1	0.00	0.00	0.00	0.00	2026-08-30 16:58:27.165997	\N
256	18	1	1	1	1	1	1	2.50	12.00	6.50	4.00	2026-08-24 22:59:44.680752	2026-08-30 17:04:32.310206
618	693	1	1	1	2	1	1	40.00	20.00	20.00	20.00	2026-09-01 06:12:38.315532	\N
\.


--
-- Data for Name: monthly_exam_schedules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.monthly_exam_schedules (id, academic_year_id, term, month, grade_id, section_id, subject_id, exam_date, day_name, period_number, created_at, updated_at) FROM stdin;
11	1	1	1	1	1	2	2026-09-02	السبت	1	2026-09-02 04:32:58.376224	\N
12	1	1	1	1	1	5	2026-09-02	السبت	1	2026-09-02 04:32:58.376224	\N
13	1	1	1	1	1	1	2026-09-02	السبت	1	2026-09-02 04:32:58.376224	\N
14	1	1	1	1	1	4	2026-09-02	السبت	1	2026-09-02 04:32:58.376224	\N
15	1	1	1	1	1	3	2026-09-02	السبت	1	2026-09-02 04:32:58.376224	\N
\.


--
-- Data for Name: notification_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notification_logs (id, notification_id, parent_id, sent_at, delivery_status, read_at, created_at, updated_at) FROM stdin;
1	2	1	2026-08-16 22:59:49.166424	read	2026-08-24 22:59:49.166442	2026-08-24 22:59:44.680752	\N
2	2	2	2026-08-17 22:59:49.166521	sent	2026-08-21 22:59:49.166525	2026-08-24 22:59:44.680752	\N
3	2	3	2026-08-14 22:59:49.166546	read	2026-08-19 22:59:49.166549	2026-08-24 22:59:44.680752	\N
4	2	4	2026-08-17 22:59:49.166567	delivered	2026-08-23 22:59:49.166569	2026-08-24 22:59:44.680752	\N
5	2	5	2026-08-16 22:59:49.166584	sent	2026-08-23 22:59:49.166586	2026-08-24 22:59:44.680752	\N
6	2	6	2026-08-16 22:59:49.1666	delivered	\N	2026-08-24 22:59:44.680752	\N
7	2	7	2026-08-20 22:59:49.166616	sent	2026-08-24 22:59:49.166617	2026-08-24 22:59:44.680752	\N
8	2	8	2026-08-23 22:59:49.166632	sent	\N	2026-08-24 22:59:44.680752	\N
9	2	9	2026-08-18 22:59:49.166647	sent	2026-08-24 22:59:49.166649	2026-08-24 22:59:44.680752	\N
10	2	10	2026-08-21 22:59:49.166662	read	2026-08-20 22:59:49.166663	2026-08-24 22:59:44.680752	\N
11	2	11	2026-08-18 22:59:49.166677	read	\N	2026-08-24 22:59:44.680752	\N
12	2	12	2026-08-21 22:59:49.166691	delivered	\N	2026-08-24 22:59:44.680752	\N
13	2	13	2026-08-20 22:59:49.166705	delivered	2026-08-22 22:59:49.166707	2026-08-24 22:59:44.680752	\N
14	2	14	2026-08-18 22:59:49.16672	delivered	2026-08-24 22:59:49.166721	2026-08-24 22:59:44.680752	\N
15	2	15	2026-08-22 22:59:49.166735	delivered	2026-08-23 22:59:49.166736	2026-08-24 22:59:44.680752	\N
16	2	16	2026-08-17 22:59:49.166749	delivered	\N	2026-08-24 22:59:44.680752	\N
17	2	17	2026-08-20 22:59:49.166763	read	\N	2026-08-24 22:59:44.680752	\N
18	2	18	2026-08-16 22:59:49.166776	delivered	2026-08-24 22:59:49.166778	2026-08-24 22:59:44.680752	\N
19	2	19	2026-08-15 22:59:49.166791	sent	2026-08-21 22:59:49.166793	2026-08-24 22:59:44.680752	\N
20	2	20	2026-08-20 22:59:49.166805	delivered	\N	2026-08-24 22:59:44.680752	\N
21	3	1	2026-08-20 22:59:49.173184	sent	\N	2026-08-24 22:59:44.680752	\N
22	3	2	2026-08-18 22:59:49.173243	sent	\N	2026-08-24 22:59:44.680752	\N
23	3	3	2026-08-16 22:59:49.173266	sent	2026-08-19 22:59:49.173268	2026-08-24 22:59:44.680752	\N
24	3	4	2026-08-17 22:59:49.173286	read	\N	2026-08-24 22:59:44.680752	\N
25	3	5	2026-08-23 22:59:49.173303	sent	2026-08-22 22:59:49.173304	2026-08-24 22:59:44.680752	\N
26	3	6	2026-08-16 22:59:49.173319	delivered	\N	2026-08-24 22:59:44.680752	\N
27	3	7	2026-08-15 22:59:49.173334	read	2026-08-22 22:59:49.173336	2026-08-24 22:59:44.680752	\N
28	3	8	2026-08-16 22:59:49.173351	read	\N	2026-08-24 22:59:44.680752	\N
29	3	9	2026-08-19 22:59:49.173365	read	2026-08-24 22:59:49.173366	2026-08-24 22:59:44.680752	\N
30	3	10	2026-08-19 22:59:49.173382	delivered	2026-08-22 22:59:49.173384	2026-08-24 22:59:44.680752	\N
31	3	11	2026-08-20 22:59:49.173398	delivered	2026-08-23 22:59:49.173399	2026-08-24 22:59:44.680752	\N
32	3	12	2026-08-23 22:59:49.173413	read	\N	2026-08-24 22:59:44.680752	\N
33	3	13	2026-08-21 22:59:49.173428	read	2026-08-22 22:59:49.17343	2026-08-24 22:59:44.680752	\N
34	3	14	2026-08-18 22:59:49.173444	sent	\N	2026-08-24 22:59:44.680752	\N
35	3	15	2026-08-22 22:59:49.173457	delivered	\N	2026-08-24 22:59:44.680752	\N
36	3	16	2026-08-17 22:59:49.173471	delivered	\N	2026-08-24 22:59:44.680752	\N
37	3	17	2026-08-15 22:59:49.173492	delivered	2026-08-23 22:59:49.173494	2026-08-24 22:59:44.680752	\N
38	3	18	2026-08-23 22:59:49.173507	delivered	2026-08-20 22:59:49.173508	2026-08-24 22:59:44.680752	\N
39	3	19	2026-08-15 22:59:49.173521	sent	\N	2026-08-24 22:59:44.680752	\N
40	3	20	2026-08-19 22:59:49.173534	read	2026-08-19 22:59:49.173536	2026-08-24 22:59:44.680752	\N
41	4	1	2026-08-19 22:59:49.175715	sent	\N	2026-08-24 22:59:44.680752	\N
42	4	2	2026-08-14 22:59:49.175761	sent	2026-08-21 22:59:49.175764	2026-08-24 22:59:44.680752	\N
43	4	3	2026-08-19 22:59:49.175783	read	2026-08-24 22:59:49.175785	2026-08-24 22:59:44.680752	\N
44	4	4	2026-08-22 22:59:49.175799	delivered	2026-08-24 22:59:49.175801	2026-08-24 22:59:44.680752	\N
45	4	5	2026-08-16 22:59:49.175814	sent	2026-08-20 22:59:49.175816	2026-08-24 22:59:44.680752	\N
46	4	6	2026-08-23 22:59:49.17583	delivered	\N	2026-08-24 22:59:44.680752	\N
47	4	7	2026-08-23 22:59:49.175845	delivered	\N	2026-08-24 22:59:44.680752	\N
48	4	8	2026-08-19 22:59:49.175859	sent	2026-08-20 22:59:49.175861	2026-08-24 22:59:44.680752	\N
49	4	9	2026-08-22 22:59:49.175875	read	\N	2026-08-24 22:59:44.680752	\N
50	4	10	2026-08-22 22:59:49.175889	sent	2026-08-21 22:59:49.175891	2026-08-24 22:59:44.680752	\N
51	4	11	2026-08-18 22:59:49.175906	read	\N	2026-08-24 22:59:44.680752	\N
52	4	12	2026-08-14 22:59:49.175919	sent	2026-08-20 22:59:49.175921	2026-08-24 22:59:44.680752	\N
53	4	13	2026-08-20 22:59:49.175934	sent	2026-08-21 22:59:49.175935	2026-08-24 22:59:44.680752	\N
54	4	14	2026-08-17 22:59:49.175949	read	\N	2026-08-24 22:59:44.680752	\N
55	4	15	2026-08-15 22:59:49.175962	read	\N	2026-08-24 22:59:44.680752	\N
56	4	16	2026-08-19 22:59:49.175976	read	\N	2026-08-24 22:59:44.680752	\N
57	4	17	2026-08-19 22:59:49.175991	delivered	2026-08-22 22:59:49.175992	2026-08-24 22:59:44.680752	\N
58	4	18	2026-08-23 22:59:49.176006	read	2026-08-20 22:59:49.176008	2026-08-24 22:59:44.680752	\N
59	4	19	2026-08-16 22:59:49.176021	read	\N	2026-08-24 22:59:44.680752	\N
60	4	20	2026-08-19 22:59:49.176035	read	\N	2026-08-24 22:59:44.680752	\N
61	5	1	2026-08-22 22:59:49.178067	delivered	2026-08-20 22:59:49.178074	2026-08-24 22:59:44.680752	\N
62	5	2	2026-08-14 22:59:49.178109	sent	\N	2026-08-24 22:59:44.680752	\N
63	5	3	2026-08-18 22:59:49.17813	sent	\N	2026-08-24 22:59:44.680752	\N
64	5	4	2026-08-19 22:59:49.178146	sent	\N	2026-08-24 22:59:44.680752	\N
65	5	5	2026-08-14 22:59:49.17816	delivered	\N	2026-08-24 22:59:44.680752	\N
66	5	6	2026-08-21 22:59:49.178174	sent	\N	2026-08-24 22:59:44.680752	\N
67	5	7	2026-08-14 22:59:49.178188	read	\N	2026-08-24 22:59:44.680752	\N
68	5	8	2026-08-21 22:59:49.178201	delivered	\N	2026-08-24 22:59:44.680752	\N
69	5	9	2026-08-19 22:59:49.178221	delivered	2026-08-20 22:59:49.178223	2026-08-24 22:59:44.680752	\N
70	5	10	2026-08-19 22:59:49.178239	delivered	\N	2026-08-24 22:59:44.680752	\N
71	5	11	2026-08-21 22:59:49.178253	read	2026-08-20 22:59:49.178255	2026-08-24 22:59:44.680752	\N
72	5	12	2026-08-17 22:59:49.178269	delivered	2026-08-20 22:59:49.17827	2026-08-24 22:59:44.680752	\N
73	5	13	2026-08-20 22:59:49.178283	delivered	2026-08-22 22:59:49.178285	2026-08-24 22:59:44.680752	\N
74	5	14	2026-08-19 22:59:49.178298	read	\N	2026-08-24 22:59:44.680752	\N
75	5	15	2026-08-21 22:59:49.178312	delivered	\N	2026-08-24 22:59:44.680752	\N
76	5	16	2026-08-20 22:59:49.178325	read	\N	2026-08-24 22:59:44.680752	\N
77	5	17	2026-08-18 22:59:49.178338	sent	\N	2026-08-24 22:59:44.680752	\N
78	5	18	2026-08-18 22:59:49.178351	delivered	2026-08-24 22:59:49.178352	2026-08-24 22:59:44.680752	\N
79	5	19	2026-08-16 22:59:49.178365	read	2026-08-23 22:59:49.178367	2026-08-24 22:59:44.680752	\N
80	5	20	2026-08-20 22:59:49.17838	delivered	2026-08-20 22:59:49.178381	2026-08-24 22:59:44.680752	\N
81	6	1	2026-08-16 22:59:49.180275	delivered	\N	2026-08-24 22:59:44.680752	\N
82	6	2	2026-08-17 22:59:49.180314	sent	2026-08-23 22:59:49.180317	2026-08-24 22:59:44.680752	\N
83	6	3	2026-08-18 22:59:49.180335	read	\N	2026-08-24 22:59:44.680752	\N
84	6	4	2026-08-19 22:59:49.180351	read	\N	2026-08-24 22:59:44.680752	\N
85	6	5	2026-08-14 22:59:49.180366	read	2026-08-23 22:59:49.180368	2026-08-24 22:59:44.680752	\N
86	6	6	2026-08-23 22:59:49.180382	sent	\N	2026-08-24 22:59:44.680752	\N
87	6	7	2026-08-20 22:59:49.180395	read	\N	2026-08-24 22:59:44.680752	\N
88	6	8	2026-08-22 22:59:49.180408	read	2026-08-22 22:59:49.180409	2026-08-24 22:59:44.680752	\N
89	6	9	2026-08-20 22:59:49.180422	sent	\N	2026-08-24 22:59:44.680752	\N
90	6	10	2026-08-21 22:59:49.180435	delivered	\N	2026-08-24 22:59:44.680752	\N
91	6	11	2026-08-18 22:59:49.180448	delivered	2026-08-23 22:59:49.180449	2026-08-24 22:59:44.680752	\N
92	6	12	2026-08-19 22:59:49.180462	sent	2026-08-20 22:59:49.180463	2026-08-24 22:59:44.680752	\N
93	6	13	2026-08-14 22:59:49.180477	sent	\N	2026-08-24 22:59:44.680752	\N
94	6	14	2026-08-16 22:59:49.18049	sent	\N	2026-08-24 22:59:44.680752	\N
95	6	15	2026-08-17 22:59:49.180503	read	2026-08-23 22:59:49.180504	2026-08-24 22:59:44.680752	\N
96	6	16	2026-08-17 22:59:49.180516	read	2026-08-24 22:59:49.180518	2026-08-24 22:59:44.680752	\N
97	6	17	2026-08-16 22:59:49.18053	delivered	2026-08-22 22:59:49.180532	2026-08-24 22:59:44.680752	\N
98	6	18	2026-08-22 22:59:49.180544	delivered	2026-08-24 22:59:49.180546	2026-08-24 22:59:44.680752	\N
99	6	19	2026-08-23 22:59:49.180558	sent	\N	2026-08-24 22:59:44.680752	\N
100	6	20	2026-08-23 22:59:49.180571	read	\N	2026-08-24 22:59:44.680752	\N
101	7	1	2026-08-30 15:56:44.812773	sent	\N	2026-08-30 15:56:44.798933	\N
102	7	2	2026-08-30 15:56:44.812977	sent	\N	2026-08-30 15:56:44.798933	\N
103	7	3	2026-08-30 15:56:44.813038	sent	\N	2026-08-30 15:56:44.798933	\N
104	7	4	2026-08-30 15:56:44.813079	sent	\N	2026-08-30 15:56:44.798933	\N
105	7	6	2026-08-30 15:56:44.813119	sent	\N	2026-08-30 15:56:44.798933	\N
106	7	7	2026-08-30 15:56:44.813158	sent	\N	2026-08-30 15:56:44.798933	\N
107	7	8	2026-08-30 15:56:44.813191	sent	\N	2026-08-30 15:56:44.798933	\N
108	7	9	2026-08-30 15:56:44.813222	sent	\N	2026-08-30 15:56:44.798933	\N
109	7	10	2026-08-30 15:56:44.813252	sent	\N	2026-08-30 15:56:44.798933	\N
110	7	11	2026-08-30 15:56:44.813282	sent	\N	2026-08-30 15:56:44.798933	\N
111	7	12	2026-08-30 15:56:44.813312	sent	\N	2026-08-30 15:56:44.798933	\N
112	7	13	2026-08-30 15:56:44.813348	sent	\N	2026-08-30 15:56:44.798933	\N
113	7	14	2026-08-30 15:56:44.81338	sent	\N	2026-08-30 15:56:44.798933	\N
114	7	15	2026-08-30 15:56:44.813411	sent	\N	2026-08-30 15:56:44.798933	\N
115	7	16	2026-08-30 15:56:44.813443	sent	\N	2026-08-30 15:56:44.798933	\N
116	7	17	2026-08-30 15:56:44.813473	sent	\N	2026-08-30 15:56:44.798933	\N
117	7	18	2026-08-30 15:56:44.813505	sent	\N	2026-08-30 15:56:44.798933	\N
118	7	19	2026-08-30 15:56:44.813533	sent	\N	2026-08-30 15:56:44.798933	\N
119	7	20	2026-08-30 15:56:44.81356	sent	\N	2026-08-30 15:56:44.798933	\N
120	7	21	2026-08-30 15:56:44.813588	sent	\N	2026-08-30 15:56:44.798933	\N
121	7	22	2026-08-30 15:56:44.813615	sent	\N	2026-08-30 15:56:44.798933	\N
122	7	23	2026-08-30 15:56:44.813643	sent	\N	2026-08-30 15:56:44.798933	\N
123	7	24	2026-08-30 15:56:44.813672	sent	\N	2026-08-30 15:56:44.798933	\N
124	7	25	2026-08-30 15:56:44.813802	sent	\N	2026-08-30 15:56:44.798933	\N
125	7	26	2026-08-30 15:56:44.813834	sent	\N	2026-08-30 15:56:44.798933	\N
126	7	27	2026-08-30 15:56:44.813864	sent	\N	2026-08-30 15:56:44.798933	\N
127	7	28	2026-08-30 15:56:44.813897	sent	\N	2026-08-30 15:56:44.798933	\N
128	7	29	2026-08-30 15:56:44.81393	sent	\N	2026-08-30 15:56:44.798933	\N
129	7	31	2026-08-30 15:56:44.813967	sent	\N	2026-08-30 15:56:44.798933	\N
130	7	32	2026-08-30 15:56:44.813997	sent	\N	2026-08-30 15:56:44.798933	\N
131	7	33	2026-08-30 15:56:44.814029	sent	\N	2026-08-30 15:56:44.798933	\N
132	7	5	2026-08-30 15:56:44.81406	sent	\N	2026-08-30 15:56:44.798933	\N
133	7	34	2026-08-30 15:56:44.814092	sent	\N	2026-08-30 15:56:44.798933	\N
134	7	35	2026-08-30 15:56:44.81412	sent	\N	2026-08-30 15:56:44.798933	\N
135	7	36	2026-08-30 15:56:44.814149	sent	\N	2026-08-30 15:56:44.798933	\N
136	7	37	2026-08-30 15:56:44.814176	sent	\N	2026-08-30 15:56:44.798933	\N
137	7	38	2026-08-30 15:56:44.814204	sent	\N	2026-08-30 15:56:44.798933	\N
138	7	39	2026-08-30 15:56:44.814232	sent	\N	2026-08-30 15:56:44.798933	\N
139	7	40	2026-08-30 15:56:44.814259	sent	\N	2026-08-30 15:56:44.798933	\N
140	7	41	2026-08-30 15:56:44.81429	sent	\N	2026-08-30 15:56:44.798933	\N
141	7	42	2026-08-30 15:56:44.814318	sent	\N	2026-08-30 15:56:44.798933	\N
142	7	43	2026-08-30 15:56:44.814346	sent	\N	2026-08-30 15:56:44.798933	\N
143	7	44	2026-08-30 15:56:44.814373	sent	\N	2026-08-30 15:56:44.798933	\N
144	7	45	2026-08-30 15:56:44.814415	sent	\N	2026-08-30 15:56:44.798933	\N
145	7	46	2026-08-30 15:56:44.814448	sent	\N	2026-08-30 15:56:44.798933	\N
146	7	47	2026-08-30 15:56:44.814477	sent	\N	2026-08-30 15:56:44.798933	\N
147	7	48	2026-08-30 15:56:44.814504	sent	\N	2026-08-30 15:56:44.798933	\N
148	7	49	2026-08-30 15:56:44.814531	sent	\N	2026-08-30 15:56:44.798933	\N
149	7	50	2026-08-30 15:56:44.814559	sent	\N	2026-08-30 15:56:44.798933	\N
150	7	51	2026-08-30 15:56:44.814588	sent	\N	2026-08-30 15:56:44.798933	\N
151	7	52	2026-08-30 15:56:44.814615	sent	\N	2026-08-30 15:56:44.798933	\N
152	7	53	2026-08-30 15:56:44.814641	sent	\N	2026-08-30 15:56:44.798933	\N
153	7	54	2026-08-30 15:56:44.814668	sent	\N	2026-08-30 15:56:44.798933	\N
154	7	55	2026-08-30 15:56:44.814697	sent	\N	2026-08-30 15:56:44.798933	\N
155	7	56	2026-08-30 15:56:44.814726	sent	\N	2026-08-30 15:56:44.798933	\N
156	7	57	2026-08-30 15:56:44.814754	sent	\N	2026-08-30 15:56:44.798933	\N
157	7	58	2026-08-30 15:56:44.814779	sent	\N	2026-08-30 15:56:44.798933	\N
158	7	59	2026-08-30 15:56:44.814807	sent	\N	2026-08-30 15:56:44.798933	\N
159	7	60	2026-08-30 15:56:44.814835	sent	\N	2026-08-30 15:56:44.798933	\N
160	7	61	2026-08-30 15:56:44.814862	sent	\N	2026-08-30 15:56:44.798933	\N
161	7	62	2026-08-30 15:56:44.814893	sent	\N	2026-08-30 15:56:44.798933	\N
162	7	63	2026-08-30 15:56:44.814918	sent	\N	2026-08-30 15:56:44.798933	\N
163	7	64	2026-08-30 15:56:44.814943	sent	\N	2026-08-30 15:56:44.798933	\N
164	7	65	2026-08-30 15:56:44.814967	sent	\N	2026-08-30 15:56:44.798933	\N
165	7	66	2026-08-30 15:56:44.814995	sent	\N	2026-08-30 15:56:44.798933	\N
166	7	67	2026-08-30 15:56:44.815021	sent	\N	2026-08-30 15:56:44.798933	\N
167	7	68	2026-08-30 15:56:44.815045	sent	\N	2026-08-30 15:56:44.798933	\N
168	7	69	2026-08-30 15:56:44.815072	sent	\N	2026-08-30 15:56:44.798933	\N
169	7	70	2026-08-30 15:56:44.815097	sent	\N	2026-08-30 15:56:44.798933	\N
170	7	71	2026-08-30 15:56:44.815121	sent	\N	2026-08-30 15:56:44.798933	\N
171	7	72	2026-08-30 15:56:44.815145	sent	\N	2026-08-30 15:56:44.798933	\N
172	7	73	2026-08-30 15:56:44.815169	sent	\N	2026-08-30 15:56:44.798933	\N
173	7	74	2026-08-30 15:56:44.815197	sent	\N	2026-08-30 15:56:44.798933	\N
174	7	75	2026-08-30 15:56:44.815222	sent	\N	2026-08-30 15:56:44.798933	\N
175	7	76	2026-08-30 15:56:44.815247	sent	\N	2026-08-30 15:56:44.798933	\N
176	7	77	2026-08-30 15:56:44.815271	sent	\N	2026-08-30 15:56:44.798933	\N
177	7	78	2026-08-30 15:56:44.815295	sent	\N	2026-08-30 15:56:44.798933	\N
178	7	79	2026-08-30 15:56:44.815321	sent	\N	2026-08-30 15:56:44.798933	\N
179	7	80	2026-08-30 15:56:44.815348	sent	\N	2026-08-30 15:56:44.798933	\N
180	7	81	2026-08-30 15:56:44.815375	sent	\N	2026-08-30 15:56:44.798933	\N
181	7	82	2026-08-30 15:56:44.815404	sent	\N	2026-08-30 15:56:44.798933	\N
182	7	83	2026-08-30 15:56:44.815431	sent	\N	2026-08-30 15:56:44.798933	\N
183	7	84	2026-08-30 15:56:44.815457	sent	\N	2026-08-30 15:56:44.798933	\N
184	7	85	2026-08-30 15:56:44.815481	sent	\N	2026-08-30 15:56:44.798933	\N
185	7	86	2026-08-30 15:56:44.815506	sent	\N	2026-08-30 15:56:44.798933	\N
186	7	87	2026-08-30 15:56:44.815535	sent	\N	2026-08-30 15:56:44.798933	\N
187	7	88	2026-08-30 15:56:44.815566	sent	\N	2026-08-30 15:56:44.798933	\N
188	7	89	2026-08-30 15:56:44.815591	sent	\N	2026-08-30 15:56:44.798933	\N
189	7	90	2026-08-30 15:56:44.815616	sent	\N	2026-08-30 15:56:44.798933	\N
190	7	91	2026-08-30 15:56:44.815641	sent	\N	2026-08-30 15:56:44.798933	\N
191	7	92	2026-08-30 15:56:44.815667	sent	\N	2026-08-30 15:56:44.798933	\N
192	7	93	2026-08-30 15:56:44.815699	sent	\N	2026-08-30 15:56:44.798933	\N
193	7	94	2026-08-30 15:56:44.815726	sent	\N	2026-08-30 15:56:44.798933	\N
194	7	95	2026-08-30 15:56:44.815751	sent	\N	2026-08-30 15:56:44.798933	\N
195	7	96	2026-08-30 15:56:44.815776	sent	\N	2026-08-30 15:56:44.798933	\N
196	7	97	2026-08-30 15:56:44.8158	sent	\N	2026-08-30 15:56:44.798933	\N
197	7	98	2026-08-30 15:56:44.815827	sent	\N	2026-08-30 15:56:44.798933	\N
198	7	99	2026-08-30 15:56:44.815852	sent	\N	2026-08-30 15:56:44.798933	\N
199	7	100	2026-08-30 15:56:44.815876	sent	\N	2026-08-30 15:56:44.798933	\N
200	7	30	2026-08-30 15:56:44.815901	sent	\N	2026-08-30 15:56:44.798933	\N
201	8	1	2026-08-30 15:57:24.752061	sent	\N	2026-08-30 15:57:24.747942	\N
202	8	2	2026-08-30 15:57:24.752201	sent	\N	2026-08-30 15:57:24.747942	\N
203	8	3	2026-08-30 15:57:24.752262	sent	\N	2026-08-30 15:57:24.747942	\N
204	8	4	2026-08-30 15:57:24.752311	sent	\N	2026-08-30 15:57:24.747942	\N
205	8	6	2026-08-30 15:57:24.752364	sent	\N	2026-08-30 15:57:24.747942	\N
206	8	7	2026-08-30 15:57:24.752414	sent	\N	2026-08-30 15:57:24.747942	\N
207	8	8	2026-08-30 15:57:24.752462	sent	\N	2026-08-30 15:57:24.747942	\N
208	8	9	2026-08-30 15:57:24.752519	sent	\N	2026-08-30 15:57:24.747942	\N
209	8	10	2026-08-30 15:57:24.752566	sent	\N	2026-08-30 15:57:24.747942	\N
210	8	11	2026-08-30 15:57:24.752613	sent	\N	2026-08-30 15:57:24.747942	\N
211	8	12	2026-08-30 15:57:24.75265	sent	\N	2026-08-30 15:57:24.747942	\N
212	8	13	2026-08-30 15:57:24.752693	sent	\N	2026-08-30 15:57:24.747942	\N
213	8	14	2026-08-30 15:57:24.752732	sent	\N	2026-08-30 15:57:24.747942	\N
214	8	15	2026-08-30 15:57:24.752771	sent	\N	2026-08-30 15:57:24.747942	\N
215	8	16	2026-08-30 15:57:24.752811	sent	\N	2026-08-30 15:57:24.747942	\N
216	8	17	2026-08-30 15:57:24.752853	sent	\N	2026-08-30 15:57:24.747942	\N
217	8	18	2026-08-30 15:57:24.752893	sent	\N	2026-08-30 15:57:24.747942	\N
218	8	19	2026-08-30 15:57:24.752937	sent	\N	2026-08-30 15:57:24.747942	\N
219	8	20	2026-08-30 15:57:24.752981	sent	\N	2026-08-30 15:57:24.747942	\N
220	8	21	2026-08-30 15:57:24.753031	sent	\N	2026-08-30 15:57:24.747942	\N
221	8	22	2026-08-30 15:57:24.753076	sent	\N	2026-08-30 15:57:24.747942	\N
222	8	23	2026-08-30 15:57:24.753122	sent	\N	2026-08-30 15:57:24.747942	\N
223	8	24	2026-08-30 15:57:24.75317	sent	\N	2026-08-30 15:57:24.747942	\N
224	8	25	2026-08-30 15:57:24.753214	sent	\N	2026-08-30 15:57:24.747942	\N
225	8	26	2026-08-30 15:57:24.753257	sent	\N	2026-08-30 15:57:24.747942	\N
226	8	27	2026-08-30 15:57:24.7533	sent	\N	2026-08-30 15:57:24.747942	\N
227	8	28	2026-08-30 15:57:24.753346	sent	\N	2026-08-30 15:57:24.747942	\N
228	8	29	2026-08-30 15:57:24.753388	sent	\N	2026-08-30 15:57:24.747942	\N
229	8	31	2026-08-30 15:57:24.75343	sent	\N	2026-08-30 15:57:24.747942	\N
230	8	32	2026-08-30 15:57:24.753469	sent	\N	2026-08-30 15:57:24.747942	\N
231	8	33	2026-08-30 15:57:24.753512	sent	\N	2026-08-30 15:57:24.747942	\N
232	8	5	2026-08-30 15:57:24.753553	sent	\N	2026-08-30 15:57:24.747942	\N
233	8	34	2026-08-30 15:57:24.753599	sent	\N	2026-08-30 15:57:24.747942	\N
234	8	35	2026-08-30 15:57:24.753643	sent	\N	2026-08-30 15:57:24.747942	\N
235	8	36	2026-08-30 15:57:24.753688	sent	\N	2026-08-30 15:57:24.747942	\N
236	8	37	2026-08-30 15:57:24.753733	sent	\N	2026-08-30 15:57:24.747942	\N
237	8	38	2026-08-30 15:57:24.753775	sent	\N	2026-08-30 15:57:24.747942	\N
238	8	39	2026-08-30 15:57:24.753811	sent	\N	2026-08-30 15:57:24.747942	\N
239	8	40	2026-08-30 15:57:24.753849	sent	\N	2026-08-30 15:57:24.747942	\N
240	8	41	2026-08-30 15:57:24.753888	sent	\N	2026-08-30 15:57:24.747942	\N
241	8	42	2026-08-30 15:57:24.753931	sent	\N	2026-08-30 15:57:24.747942	\N
242	8	43	2026-08-30 15:57:24.753974	sent	\N	2026-08-30 15:57:24.747942	\N
243	8	44	2026-08-30 15:57:24.754015	sent	\N	2026-08-30 15:57:24.747942	\N
244	8	45	2026-08-30 15:57:24.754059	sent	\N	2026-08-30 15:57:24.747942	\N
245	8	46	2026-08-30 15:57:24.7541	sent	\N	2026-08-30 15:57:24.747942	\N
246	8	47	2026-08-30 15:57:24.75414	sent	\N	2026-08-30 15:57:24.747942	\N
247	8	48	2026-08-30 15:57:24.754181	sent	\N	2026-08-30 15:57:24.747942	\N
248	8	49	2026-08-30 15:57:24.754222	sent	\N	2026-08-30 15:57:24.747942	\N
249	8	50	2026-08-30 15:57:24.754268	sent	\N	2026-08-30 15:57:24.747942	\N
250	8	51	2026-08-30 15:57:24.754308	sent	\N	2026-08-30 15:57:24.747942	\N
251	8	52	2026-08-30 15:57:24.754354	sent	\N	2026-08-30 15:57:24.747942	\N
252	8	53	2026-08-30 15:57:24.754398	sent	\N	2026-08-30 15:57:24.747942	\N
253	8	54	2026-08-30 15:57:24.754432	sent	\N	2026-08-30 15:57:24.747942	\N
254	8	55	2026-08-30 15:57:24.754471	sent	\N	2026-08-30 15:57:24.747942	\N
255	8	56	2026-08-30 15:57:24.754506	sent	\N	2026-08-30 15:57:24.747942	\N
256	8	57	2026-08-30 15:57:24.754545	sent	\N	2026-08-30 15:57:24.747942	\N
257	8	58	2026-08-30 15:57:24.754585	sent	\N	2026-08-30 15:57:24.747942	\N
258	8	59	2026-08-30 15:57:24.75462	sent	\N	2026-08-30 15:57:24.747942	\N
259	8	60	2026-08-30 15:57:24.754653	sent	\N	2026-08-30 15:57:24.747942	\N
260	8	61	2026-08-30 15:57:24.754688	sent	\N	2026-08-30 15:57:24.747942	\N
261	8	62	2026-08-30 15:57:24.754724	sent	\N	2026-08-30 15:57:24.747942	\N
262	8	63	2026-08-30 15:57:24.754755	sent	\N	2026-08-30 15:57:24.747942	\N
263	8	64	2026-08-30 15:57:24.754779	sent	\N	2026-08-30 15:57:24.747942	\N
264	8	65	2026-08-30 15:57:24.754802	sent	\N	2026-08-30 15:57:24.747942	\N
265	8	66	2026-08-30 15:57:24.754829	sent	\N	2026-08-30 15:57:24.747942	\N
266	8	67	2026-08-30 15:57:24.754853	sent	\N	2026-08-30 15:57:24.747942	\N
267	8	68	2026-08-30 15:57:24.754878	sent	\N	2026-08-30 15:57:24.747942	\N
268	8	69	2026-08-30 15:57:24.7549	sent	\N	2026-08-30 15:57:24.747942	\N
269	8	70	2026-08-30 15:57:24.754923	sent	\N	2026-08-30 15:57:24.747942	\N
270	8	71	2026-08-30 15:57:24.754948	sent	\N	2026-08-30 15:57:24.747942	\N
271	8	72	2026-08-30 15:57:24.754971	sent	\N	2026-08-30 15:57:24.747942	\N
272	8	73	2026-08-30 15:57:24.754995	sent	\N	2026-08-30 15:57:24.747942	\N
273	8	74	2026-08-30 15:57:24.755019	sent	\N	2026-08-30 15:57:24.747942	\N
274	8	75	2026-08-30 15:57:24.755043	sent	\N	2026-08-30 15:57:24.747942	\N
275	8	76	2026-08-30 15:57:24.755068	sent	\N	2026-08-30 15:57:24.747942	\N
276	8	77	2026-08-30 15:57:24.755091	sent	\N	2026-08-30 15:57:24.747942	\N
277	8	78	2026-08-30 15:57:24.755115	sent	\N	2026-08-30 15:57:24.747942	\N
278	8	79	2026-08-30 15:57:24.75514	sent	\N	2026-08-30 15:57:24.747942	\N
279	8	80	2026-08-30 15:57:24.755165	sent	\N	2026-08-30 15:57:24.747942	\N
280	8	81	2026-08-30 15:57:24.755188	sent	\N	2026-08-30 15:57:24.747942	\N
281	8	82	2026-08-30 15:57:24.755212	sent	\N	2026-08-30 15:57:24.747942	\N
282	8	83	2026-08-30 15:57:24.755235	sent	\N	2026-08-30 15:57:24.747942	\N
283	8	84	2026-08-30 15:57:24.755258	sent	\N	2026-08-30 15:57:24.747942	\N
284	8	85	2026-08-30 15:57:24.755282	sent	\N	2026-08-30 15:57:24.747942	\N
285	8	86	2026-08-30 15:57:24.755305	sent	\N	2026-08-30 15:57:24.747942	\N
286	8	87	2026-08-30 15:57:24.755328	sent	\N	2026-08-30 15:57:24.747942	\N
287	8	88	2026-08-30 15:57:24.755355	sent	\N	2026-08-30 15:57:24.747942	\N
288	8	89	2026-08-30 15:57:24.755379	sent	\N	2026-08-30 15:57:24.747942	\N
289	8	90	2026-08-30 15:57:24.755405	sent	\N	2026-08-30 15:57:24.747942	\N
290	8	91	2026-08-30 15:57:24.755428	sent	\N	2026-08-30 15:57:24.747942	\N
291	8	92	2026-08-30 15:57:24.755451	sent	\N	2026-08-30 15:57:24.747942	\N
292	8	93	2026-08-30 15:57:24.755475	sent	\N	2026-08-30 15:57:24.747942	\N
293	8	94	2026-08-30 15:57:24.755498	sent	\N	2026-08-30 15:57:24.747942	\N
294	8	95	2026-08-30 15:57:24.755521	sent	\N	2026-08-30 15:57:24.747942	\N
295	8	96	2026-08-30 15:57:24.755544	sent	\N	2026-08-30 15:57:24.747942	\N
296	8	97	2026-08-30 15:57:24.755568	sent	\N	2026-08-30 15:57:24.747942	\N
297	8	98	2026-08-30 15:57:24.755592	sent	\N	2026-08-30 15:57:24.747942	\N
298	8	99	2026-08-30 15:57:24.755615	sent	\N	2026-08-30 15:57:24.747942	\N
299	8	100	2026-08-30 15:57:24.755638	sent	\N	2026-08-30 15:57:24.747942	\N
300	8	30	2026-08-30 15:57:24.755662	sent	\N	2026-08-30 15:57:24.747942	\N
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notifications (id, title, message, notification_type, sender_user_id, target_type, target_grade_id, target_section_id, scheduled_at, sent_at, is_active, created_at, updated_at) FROM stdin;
1	a	a	عام	2	all	\N	\N	\N	2026-08-22 05:42:48.245466	t	2026-08-22 05:42:48.237085	2026-08-22 05:42:48.237085
2	بداية العام الدراسي	نرحب بجميع الطلاب وأولياء الأمور في العام الدراسي الجديد	عام	1	all	\N	\N	\N	2026-08-20 22:59:48.935391	t	2026-08-24 22:59:44.680752	\N
3	اجتماع أولياء الأمور	سيتم عقد اجتماع لأولياء الأمور يوم الخميس القادم	عام	1	all	\N	\N	\N	2026-08-15 22:59:49.166819	t	2026-08-24 22:59:44.680752	\N
4	تأجيل اختبار	تم تأجيل اختبار الرياضيات إلى الأسبوع القادم	نتائج	1	all	\N	\N	\N	2026-08-16 22:59:49.173549	t	2026-08-24 22:59:44.680752	\N
5	تذكير بالرسوم	نذكركم بموعد استحقاق القسط الثاني من الرسوم	رسوم	1	all	\N	\N	\N	2026-08-15 22:59:49.176049	t	2026-08-24 22:59:44.680752	\N
6	فعالية مدرسية	ستقام فعالية اليوم المفتوح يوم السبت القادم	عام	1	all	\N	\N	\N	2026-08-19 22:59:49.178395	t	2026-08-24 22:59:44.680752	\N
7	حضور	قق	عام	2	all	\N	\N	\N	2026-08-30 15:56:44.816085	t	2026-08-30 15:56:44.798933	2026-08-30 15:56:44.798933
8	ث	ث	عام	2	all	\N	\N	\N	2026-08-30 15:57:24.75584	t	2026-08-30 15:57:24.747942	2026-08-30 15:57:24.747942
\.


--
-- Data for Name: parent_devices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.parent_devices (id, parent_id, device_token, device_type, app_version, last_login, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: parents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.parents (id, full_name, primary_phone, secondary_phone, address, job, category, password_hash, created_at, updated_at) FROM stdin;
1	سلطان خالد	773182401	773213851	الحي - الشرقية - تعز	طبيب	عادي	1fa940b6f9e4f6d80afed7ae45c60b6c$6a801020d4688d6fdf177f85bd7913d46aa7710523528ae14dbe0033c66c7d63	2026-08-24 22:59:44.680752	\N
2	خالد محمد	779105195	\N	الحي - الجنوبية - تعز	مزارع	عادي	d6f6154e911806c3366ed3fd17a30bc8$71ce5d1f3573deace9ff35b658f249bfaa718d4ff0de6a0b87edb76e16c9a2b0	2026-08-24 22:59:44.680752	\N
3	بدر عمر	775644418	779646426	القرية - الشمالية - إب	موظف حكومي	عادي	6977ea4ca2f809577346a07e8b591584$e2da13b2ff228da1e24b480f39e127d0bff569b5b95d34a585a13622bc6cc6b6	2026-08-24 22:59:44.680752	\N
4	راشد محمد	770704864	\N	الحارة - الشرقية - صنعاء	طبيب	عادي	ec5c79f575e168b2b57ca2337af069b2$8bb8e31c7dd2056ee8f350e17f4f6a63aa4138d4ef8171f68604490cc0554411	2026-08-24 22:59:44.680752	\N
6	سعيد محمد	776891822	\N	الحارة - الشرقية - تعز	طبيب	عادي	3b4d86e18e602cc2a47e6ae310a5ab21$16043e12b919078fd30c2e6651c12f5a450afd9f7b90ea9234f6773b589e21af	2026-08-24 22:59:44.680752	\N
7	أنس محمد	774392461	778200975	القرية - المركز - حضرموت	طبيب	عادي	fed068745232de76b232b99b84c23481$3be356388625c0dc40b6c94647f7b3f641a609de2541cf40a958d637eafa29f4	2026-08-24 22:59:44.680752	\N
8	أنس عمر	779495645	\N	الشارع - الجنوبية - إب	سائق	كفالة	7f4707d9af92e3cfa5241869637a6105$04b5316cd024e4228a0f1838857c4d34b092e1f568917d40f00a21ac2adb71a0	2026-08-24 22:59:44.680752	\N
9	بدر خالد	774821210	\N	الشارع - الشمالية - تعز	مهندس	عادي	f4a4640a5cbc958341e17f1ae16fe899$715a62244e90dc2eace6ffa893d52d213f091e3d0880c0fa378f09a89ef0d1a1	2026-08-24 22:59:44.680752	\N
10	بدر محمد	770529955	776943665	الشارع - الجنوبية - الحديدة	طبيب	عادي	6d1c0720a187ca3185e991622a8abbe5$ca09430e19127fb67e93be6c7f4edc4164e88626ef7de52c8800de45f5c10297	2026-08-24 22:59:44.680752	\N
11	بلال علي	777766472	773636879	الحي - الشمالية - إب	موظف حكومي	عادي	f7218b4d54d742e46e5066d76169c481$ffd0f2a3fdf01e88b9ccfdd1dc9663d377813a6243f835f38abd0fbf1799489b	2026-08-24 22:59:44.680752	\N
12	بلال يوسف	772831769	\N	الشارع - المدينة - الحديدة	مهندس	عادي	0ae24c274fcbb2bfa25d38aac5a6e529$f1f472a2ff229300be724dca2ffb5e77cd0dd67cb5bea3086d9dd818a65b3679	2026-08-24 22:59:44.680752	\N
13	خالد عمر	770916954	771887382	القرية - الغربية - عدن	مقاول	عادي	af24588ab1d35207221106cff09290f3$92531f56d133927c57d1dc28a480662c9c39d790cfa18a6f5b00655d789d4a23	2026-08-24 22:59:44.680752	\N
14	ناصر يوسف	773213383	\N	الحارة - المدينة - الحديدة	معلم	كفالة	894bfb7c926bcaf8c9571ed37c9c10eb$a15f83fe3f8e24fe12e1a66854e4f6cccec53db6296eb0a1ee413ad80cf257fc	2026-08-24 22:59:44.680752	\N
15	عبدالله محمد	770596566	776179223	الحي - الشمالية - المكلا	مزارع	VIP	a08e07d2e56f282efdb4c3dbcb8b1fee$6fdbab3762a13324d8b41daad7bca5d5e227a24f7a9d382c00a27d0fc4f40f08	2026-08-24 22:59:44.680752	\N
16	محمد محمد	770973407	\N	المنطقة - المدينة - الحديدة	معلم	VIP	a1220588dcb4b7731009eb4943bddeb4$5f85e0f0126ba680dd1d026d51c5007a9b69419c88bad1aab2cde4522be2d69b	2026-08-24 22:59:44.680752	\N
17	محمود يوسف	776652636	777877583	المنطقة - الشمالية - ذمار	مهندس	عادي	c2827e97536ec2b53551002b71d300a8$954d77d74c907cdc97266be20705492babdf78a20c80ee4c29fe496fa2548c83	2026-08-24 22:59:44.680752	\N
18	ناصر خالد	773236952	\N	الحارة - المدينة - المكلا	طبيب	VIP	917aa2de3e335f374d66b8ac1cad030c$a69361a6ec3bd869b141d07d6009e0c943577602e08f4412da63524fcf42941e	2026-08-24 22:59:44.680752	\N
19	بلال علي	779946200	\N	الحي - المدينة - الحديدة	مقاول	عادي	aa49e0fe64115ca4aad2ce1cbfea07b1$38d51888ca17a9172f58bd160398514862533f6830deb6a009f667535d6caf75	2026-08-24 22:59:44.680752	\N
20	خالد عمر	779618139	\N	القرية - المدينة - صنعاء	معلم	عادي	c9f48707e7b5e3aba968a4e7dfec7a27$bb35b3caadf948c5c1ee05bb27366761c7db92cc75c853f047557460eae53d31	2026-08-24 22:59:44.680752	\N
21	سلطان يوسف	774466826	\N	الحارة - الغربية - حضرموت	مهندس	كفالة	5846c46eaedb22ae915f0ce919403544$b2fb3c7731eecd6b47248f8686fbab4fa3a8085a6336b726f4280d7b85f6ca19	2026-08-24 22:59:44.680752	\N
22	محمود عمر	771687816	776232441	المنطقة - الغربية - إب	تاجر	VIP	78e88d0ccc542f1d3cc323da830fa2b5$3128b76709a0154a8e364931a6400ccd1eea30d4f32319f987ca3aa2171f8208	2026-08-24 22:59:44.680752	\N
23	أحمد علي	775404745	\N	المنطقة - الشمالية - عدن	تاجر	عادي	37082d61f6c674147938c3dda487ae4f$e0307c5815b86c6f8c8195570c9014f3a0eac586ab6509776b27dbace3b8fbdb	2026-08-24 22:59:44.680752	\N
24	وليد محمد	776230842	\N	الشارع - الجنوبية - إب	سائق	عادي	ee2dacb2ee54a2726cc1445e53160244$288015154403d4bf577f328f72d927d1a3a4561cc5d7ed21b651d9183bac1eb7	2026-08-24 22:59:44.680752	\N
25	راشد محمد	779172235	\N	الشارع - المركز - ذمار	معلم	كفالة	e88faa0af116048c36f4c84dbfaccb78$35d6ddd0dc6f318591151e4236e6f580c28f1455fc10daf9727db5d78ac3802b	2026-08-24 22:59:44.680752	\N
26	سلطان يوسف	772753274	\N	القرية - المركز - تعز	سائق	VIP	8697c10ded1a46b95cf49f02c52be35b$298d0f6158ef45c1515b92ccf82115793073c4f957a94ae9441f44814ec6f583	2026-08-24 22:59:44.680752	\N
27	وليد خالد	773514928	775408151	المنطقة - الشرقية - صنعاء	مقاول	عادي	bee4ec767d5907c0f49922df25cd0675$0f13b2f9311e6e16398ddcffd5078e9648172db800313d23ff3fefb0d8eb89f2	2026-08-24 22:59:44.680752	\N
28	وليد خالد	779927180	\N	القرية - المركز - الحديدة	تاجر	عادي	c8d9262eab7b28e042307e9c7a00647b$31371113ffc3cf6f233778e36ed420fe2782585b3aac9bb633aa1a43e4e54ce9	2026-08-24 22:59:44.680752	\N
29	خالد خالد	774308997	\N	الحارة - الجنوبية - ذمار	مزارع	عادي	b3390c9bdd8a68eb9e7352a63552240c$c7954865e324050909c63088052111bad90b4cc7d4a8eb8d72c47a7ad06e9c91	2026-08-24 22:59:44.680752	\N
31	فهد محمد	770894127	\N	الحارة - الغربية - حضرموت	مزارع	كفالة	7181f899736ed8ce5cd47f531bffc95c$193e82b68447044a5bbc9d3b624281cdfa0bfc1eeacdb49cd9094e5a5cd7c0cc	2026-08-24 22:59:44.680752	\N
32	خالد حسن	779887612	\N	الشارع - الشمالية - تعز	سائق	كفالة	52f8e6457e03458974d6c010e5367a9a$ef13960405b09b735a34220137bffd2b08562018067eb2cc77ea8ef2bcb812ba	2026-08-24 22:59:44.680752	\N
33	حسن حسن	776996689	\N	الحارة - الشمالية - حضرموت	مقاول	عادي	f3829652b7f83c61b3f8f82dfa139d4d$8ff893d270186f356760922bcae65396188889381d4091d794f69ae7da36d579	2026-08-24 22:59:44.680752	\N
5	إبراهيم محمد	774525677	779545510	الشارع - المركز - إب	مزارع	VIP	548fb1682cf8ab32f783abe2b0284820$8b1c75a915e9101da7ebc752940d37f097b675e77cbe1aaebf958bc94d8658a3	2026-08-24 22:59:44.680752	2026-08-27 01:23:02.559598
34	زياد علي	773537881	\N	الحارة - الشمالية - حضرموت	سائق	عادي	43bf124d5b19088f3d906112b026659f$1181c3a0a3f79b8c217dff95abbaf601354bd8f4ed236a33e33a5ab5d676dcbb	2026-08-24 22:59:44.680752	\N
35	بدر محمد	776248141	774283996	القرية - الغربية - حضرموت	مقاول	كفالة	c14bd49e14860d40bc34ff2a84d2fc8d$30333f84f11fa38cf350a553c033f01a0de19647cf6e25849eca48e88a0a2655	2026-08-24 22:59:44.680752	\N
36	إبراهيم خالد	772664917	770988213	الشارع - المدينة - الحديدة	مزارع	VIP	c9326dabacd5b07434c226c0846ddec8$6da20ee99187bc5e865d9d7e8439ea96abc58450af131d3b966eeaff7c4e1bcb	2026-08-24 22:59:44.680752	\N
37	إبراهيم حسن	775108357	771516352	المنطقة - المركز - المكلا	تاجر	عادي	682f24974ac2efd1b0a407ae5528ff50$88b2a5f25e8eb3a9e0afea95c0bf49e2948bb37a90528502a0e6a94b7c4bda99	2026-08-24 22:59:44.680752	\N
38	يوسف خالد	778605796	770801323	الشارع - الشرقية - إب	معلم	عادي	0ef7d665292291421ad3bf845c4ae94d$00e8dcfcf99cd1b1dd61225696b95750e470f67f05c45455e2d74623b0782c8b	2026-08-24 22:59:44.680752	\N
39	أنس يوسف	777538256	\N	المنطقة - الشرقية - عدن	طبيب	عادي	153cd184116583618d639d02f3a2f20d$2f641bc0c9b2ef03d48936698d20136e9058bcd26b6e5acf63f429a59331df74	2026-08-24 22:59:44.680752	\N
40	فهد علي	772563930	\N	المنطقة - المركز - الحديدة	سائق	عادي	6ec1baf703c8073aa6fca48171ed5919$2a5efb01121147e733c61c6a653f7d9ecfc5c68a23673ef394e7613d4224bf3c	2026-08-24 22:59:44.680752	\N
41	بدر علي	777403401	\N	الحي - المدينة - ذمار	معلم	VIP	cc7d0da75904ada0f03275fce05842aa$7c804eb1a9dca2d0d895425db3b2189ccf7a221bff0e8755dcb5aa813341ae4d	2026-08-24 22:59:44.680752	\N
42	ماجد خالد	778186518	777772886	القرية - المدينة - حضرموت	معلم	VIP	51408b1b1d13d4b366ddf30d4681352b$7550c398c6b7edf9cb2fac10043f86d6f145696bc09ddd66bb6a35288cb07437	2026-08-24 22:59:44.680752	\N
43	وليد خالد	777345106	771459114	الحي - الشمالية - عدن	موظف حكومي	عادي	1ae5f14c0dff0c564d2f6aa0f5789021$478fc200f497dbdaf8fdff1090ec65715d53ed93b795b3459c1d1996b6a11920	2026-08-24 22:59:44.680752	\N
44	أحمد عمر	777976612	\N	المنطقة - الجنوبية - عدن	مهندس	كفالة	be899f2f2962b81b357b02bc747b820a$ac463d0931d09dfe5a3b9c2a18b7c65c8002b919483f8fd234bc728cc62f9914	2026-08-24 22:59:44.680752	\N
45	عمر عمر	772243215	\N	الحي - الجنوبية - إب	مزارع	VIP	fb965dbccfaacd5259ae6cfc99758833$8d594a668987b36c0e0191ffe2c3e1433171a95523e59fc4944ac7b53245a425	2026-08-24 22:59:44.680752	\N
46	أحمد يوسف	776898647	\N	الشارع - الشمالية - تعز	مقاول	كفالة	74d71bdbdf1b3331ce815bdd31d37e68$75b53d71b1025e56619a1e2420cd9233a66d939536bcf22e2bf61ca25efb2c72	2026-08-24 22:59:44.680752	\N
47	علي يوسف	778764692	\N	الشارع - المركز - تعز	تاجر	عادي	ecd01a67886d823c74a3e4fd20623765$fe741c00ee1ad6d37dba93ee74f2aceb4eeeeb5033d3114c92fef8dd61842183	2026-08-24 22:59:44.680752	\N
48	عمر حسن	776881115	772429599	الشارع - المركز - ذمار	مقاول	كفالة	6f614bb00e58f8a6d3e04887175c70da$501a5b613e10b7fb31aa4572ff57ff35228e3b2190626dfa39f4be67f0204d92	2026-08-24 22:59:44.680752	\N
49	عبدالله علي	774493156	771380959	المنطقة - المدينة - المكلا	طبيب	كفالة	4fb31d4e60c7d9a4103e72a8728a817d$55b5a317ea0c2d32f53ad869f1e5cf80a4993c472627599df0801a35c233e0f2	2026-08-24 22:59:44.680752	\N
50	بلال حسن	774706613	\N	المنطقة - الشمالية - المكلا	مزارع	عادي	46f3f2cf4507786bace6040f3f0fb916$5505a1a0ee73f00cacec02aad24dbe6e1986e4ce76eec634730156241c68df50	2026-08-24 22:59:44.680752	\N
51	محمد محمد	778125746	773977968	الشارع - المركز - إب	سائق	عادي	fb51d20402511839925c512ba4d6b498$f0bff915a6bd8728e884c72be6a10868e6c520d3a94406e30577e5cc889b3bfc	2026-08-24 22:59:44.680752	\N
52	خالد حسن	774136668	\N	الشارع - الشمالية - ذمار	طبيب	عادي	d8c45d945607d80e089119db8a984e4e$ac4bf21f4bc38059561b6a423ff88b450f28384c726de3cea88d8967af62b13e	2026-08-24 22:59:44.680752	\N
53	وليد يوسف	779814289	\N	الحي - الشرقية - صنعاء	مقاول	عادي	d72dbabd5e03137771ac4d7271ded77e$d41b0793f651e490fbfdd70a44272bc879c38c7f9d4bcf4e3a70403f95bb024c	2026-08-24 22:59:44.680752	\N
54	علي محمد	778145809	\N	المنطقة - الغربية - الحديدة	تاجر	كفالة	1f360968537392cb8571dacaf9bf97fc$35883c03c9afa5f8fec3d3d4a145e8976f6662405ad98e449ea5859217d1e5e2	2026-08-24 22:59:44.680752	\N
55	فهد حسن	777849140	\N	المنطقة - الغربية - ذمار	طبيب	عادي	21e0d12ccc0aa418c49683cc342f42b3$dc4808e38fd0fcfd896b5c350ac400a62723086b491e9358a050c5e5766808e8	2026-08-24 22:59:44.680752	\N
56	تميم علي	772304765	770266131	المنطقة - الغربية - حضرموت	سائق	كفالة	5f71793b59dc613df807a7633d53cfdf$870defbde57f9e8a8b294d9452619dd74e83113708840b029c9b6b92c4448312	2026-08-24 22:59:44.680752	\N
57	عبدالله علي	774293154	\N	الحي - الجنوبية - تعز	مقاول	VIP	20aeb687e99079d3c816f1870537fd3b$80efc9120374e40f83aa15cb95c84c7760d0bebaac6065aee8105ab166562c39	2026-08-24 22:59:44.680752	\N
58	عمر عمر	770328771	\N	الحي - المركز - الحديدة	موظف حكومي	كفالة	adf761c63114c4d34aa594f7fad53bd8$1d1be439c5bb6d753637d2725a60608ac2d2a4e64534dee8daa751c23b409ca6	2026-08-24 22:59:44.680752	\N
59	فهد حسن	779444539	779186242	الشارع - المركز - الحديدة	موظف حكومي	VIP	6ea141f81d89c906620ad2f6bfb30481$c7fa27c76e3b63ffd88f32cbd2fd24ae9fb41b9dfc7f115b524db5795bef67db	2026-08-24 22:59:44.680752	\N
60	خالد يوسف	777406133	\N	القرية - الغربية - صنعاء	مزارع	VIP	e7bb0c47da282c233cb6e2e0d448b6c7$6d17c432b456240a6f0156c514f3f8b4b9bdff43e1b30d858bd4cd535cd5c307	2026-08-24 22:59:44.680752	\N
61	وليد عمر	777312531	\N	الحارة - الجنوبية - الحديدة	سائق	عادي	59af7933ba19c075323b9d13c7e384b9$c90341077666b00cfdee339fdceb9bc9f6725a3170d4a10bbd6cedae7bfd776a	2026-08-24 22:59:44.680752	\N
62	أحمد محمد	776631753	\N	الشارع - المدينة - عدن	مقاول	عادي	a95c8077e73c89984db3aa3bdd9182e7$1ced3dc6353187bdce6b86474957b2ec91fb8beae25c456f3f7115de9adf0ff1	2026-08-24 22:59:44.680752	\N
63	بلال عمر	773277255	770955253	الحارة - الشرقية - عدن	مزارع	كفالة	3434bf9b1560d6d8e4bbdefb2061a86c$665693a0ab1527651c8638aa4dc74f922cfb31b14e3424dd2fd24fbf2c0a5fac	2026-08-24 22:59:44.680752	\N
64	سعيد عمر	770987760	\N	الحارة - الشرقية - الحديدة	طبيب	عادي	b896497b826a0be6f740c40a5b7f8837$75d327f8f0145083cac43cee261c5617595d264ead1ba95e8539076dff3aa049	2026-08-24 22:59:44.680752	\N
65	علي يوسف	777601492	\N	الحارة - الشرقية - إب	موظف حكومي	عادي	8e85b10273024133bcf81f0cd80f1ddf$fdeb9a9e46f117b0db38f44b54e38e2f50ae812b73498be4362c45abe8008a4b	2026-08-24 22:59:44.680752	\N
66	ناصر يوسف	779395287	\N	القرية - المركز - إب	مهندس	عادي	70145f46d2235ebcbfe044143cae4fca$d372654d2184f0eb9e45ba702beb3e155a33fc9d4d979856991c8f71637a2ebe	2026-08-24 22:59:44.680752	\N
67	يوسف حسن	771465984	777504809	القرية - المدينة - إب	معلم	عادي	2c2c34b82b9a369d1f9b1cfe0e92dde9$d26c6ec19b19ce4cb97f39f40e481524d8384aa25ae8814b685447c880e3a471	2026-08-24 22:59:44.680752	\N
68	زياد عمر	774596101	\N	الحي - الغربية - ذمار	مهندس	VIP	ff75844c6b889603c933511df80e593d$42e9f2105cda389acc4e2fb55faac6311b1462f0dbdd86aaa06f38de129150f8	2026-08-24 22:59:44.680752	\N
69	زياد علي	778885549	\N	الحارة - المدينة - إب	تاجر	عادي	bee1e0670ee2f4897c79355d5db63d58$ddcbc05a9996fd9611c5805951fbc61e45b8049a0ab296596a83291e2087cf45	2026-08-24 22:59:44.680752	\N
70	فهد محمد	777604275	773404330	الحارة - المركز - صنعاء	مزارع	VIP	ad619daff2d12ffb2cf59e58d24befed$7a25d1c44dd0060f65ad2e623f9daf9923adea113eba785fa4867a3a99d8b077	2026-08-24 22:59:44.680752	\N
71	عمر علي	773826269	\N	الشارع - المركز - الحديدة	تاجر	عادي	facf441eeb1f5b3103f26d94e83de5f5$48ea00b7279b3bc854c00b710ccb08b27fe8604e486b418c54e6d7f9591ee92f	2026-08-24 22:59:44.680752	\N
72	ماجد عمر	779614113	\N	الحارة - المركز - المكلا	مهندس	عادي	3402c6bcdd12e7bf44f3c24b5ccfca59$d5ffa51b40efc325b5a7b25e685e08ae89081c859ed53c312fe33149fd06f895	2026-08-24 22:59:44.680752	\N
73	عمر يوسف	771546551	\N	المنطقة - الجنوبية - ذمار	مهندس	عادي	833a76bc09c1c69be555e4a8ac9c709b$10927ab3fb537ef1a5e774d6d2751c7fa11d0d4a0a46504959cd4f0b41fa82fb	2026-08-24 22:59:44.680752	\N
74	محمود محمد	774749637	\N	القرية - المركز - الحديدة	موظف حكومي	كفالة	1e91abd23fff0dd17a10b45af1706e4d$e925e98c627e1165081e5206fdfcc300f752399e761ece86f4adc9badc9c2d16	2026-08-24 22:59:44.680752	\N
75	بدر عمر	771630882	\N	الشارع - الجنوبية - حضرموت	مزارع	كفالة	e10dfb0c7c883f44fdf9f075a2c78e58$665f7402a6e6796c5c2d162ab1f1acd1a23dda5fa8a8e6383c4d7042659c859b	2026-08-24 22:59:44.680752	\N
76	سلطان محمد	779429493	\N	المنطقة - المدينة - صنعاء	موظف حكومي	عادي	714c1c7f1046ae28a6f8e7baeac02982$973f00b7af0964ec0d38243f81ae99864351daba1bf0091b2b96802b402b78b3	2026-08-24 22:59:44.680752	\N
77	فهد يوسف	774882196	\N	المنطقة - المدينة - تعز	موظف حكومي	عادي	52562dc47893b771e57bc42789430558$dbaa913e469a76ae4b046e2424280c0040a261bcf6db553e004c73db997de2c4	2026-08-24 22:59:44.680752	\N
78	ماجد عمر	777585254	\N	الحارة - الجنوبية - الحديدة	مزارع	VIP	15e94c10475e2aa5c7458f3a9b78741a$450e31515f93c958d5aa8a8bb8a0cfe7f97d8ffe5ba802ec2728e79cc35231f3	2026-08-24 22:59:44.680752	\N
79	محمد علي	778990793	\N	الشارع - المدينة - حضرموت	موظف حكومي	كفالة	5bf324ed2e0d19a16e469012542677ba$8153f1572cee7e6c98129f3d3d52698232a644a2c4d68723f7c3c5673ea3da0c	2026-08-24 22:59:44.680752	\N
80	سلطان علي	772391422	\N	الحي - الشمالية - تعز	مزارع	عادي	ce3307dcbbac8ea66cd45cb928e9f2d2$d9174886e3aa230c0376239ca06fde032f367404d465d7e8eb4253f939fcc602	2026-08-24 22:59:44.680752	\N
81	عمر علي	774263690	777616299	المنطقة - الغربية - الحديدة	سائق	VIP	4a23acf5c38760819581801579abe6f5$2bbc8f39ddb894ed8e7c9b064393c1c04ba6f705ae7994570d9463b45514b2ce	2026-08-24 22:59:44.680752	\N
82	زياد حسن	773469654	\N	الحي - الغربية - الحديدة	طبيب	عادي	6c938faf8a3e1e97c400be7c7b21d7b3$78c2d2c3db9d265eee79f1d696d109a84082153727f5e7d050bcb146e48bee17	2026-08-24 22:59:44.680752	\N
83	حسن علي	772965692	779138450	الحي - الغربية - عدن	مهندس	عادي	09d218af9b91be16720fdeef449ce2b6$2c0942cd18210bcba88cc221ae8ff52e23cd0819c4873ec2f6c42f0e009958ff	2026-08-24 22:59:44.680752	\N
84	راشد حسن	771936663	\N	الحارة - الجنوبية - إب	مهندس	عادي	91653ab12061bc8bff3f9b26032adaf3$28c0437dd457963b89f2ad7bbb4d2f09ef6b16d2f5f3b2538c001160c28695f6	2026-08-24 22:59:44.680752	\N
85	محمد علي	778284384	\N	الحارة - الشرقية - ذمار	معلم	كفالة	a1e450f0bcd43fae6c7668af4e9cc49a$13353ec4162edf9477b8f3befd0c314f07b1d040382aa3baaa53bb14b7439002	2026-08-24 22:59:44.680752	\N
86	طلال خالد	777407611	778563385	الحي - المركز - ذمار	طبيب	VIP	a12eb3f8f8d72b52d6c0f8d7dd206dc1$ccd6ce7b481e906df29b165011d9938f2a7aa1edf66edc85a0839b5641d65446	2026-08-24 22:59:44.680752	\N
87	إبراهيم محمد	776554598	\N	القرية - الشمالية - ذمار	مهندس	كفالة	46f775185c489fa3658a124e1fadbea4$95222340715e9e3ae81977ef9868ada3cdeddb979bb3cf5ca4bf87ad27c3e314	2026-08-24 22:59:44.680752	\N
88	زياد محمد	770248774	\N	المنطقة - المركز - الحديدة	مهندس	عادي	350306a6e4d9ca9dee7257c9fae82ffc$c32987fb3a4801960c16841a722fb7941878b1e409bc740c932e7f822f604539	2026-08-24 22:59:44.680752	\N
89	ناصر علي	771788867	777712857	القرية - الغربية - المكلا	سائق	كفالة	ce1304f496c84417ffe578bdd8a92442$c45a6cf4f4ac0ffa71477bd780dc57a8b7470ae19e9275a887923a6556681a05	2026-08-24 22:59:44.680752	\N
90	بدر خالد	770747766	774235112	القرية - المدينة - المكلا	تاجر	VIP	a6283c37b4d6ce3b95ff0040c5fd063d$41eecc231efa89d81d57d8a31fa088cf2232b5859a11a2f3a58c7fa8932b754b	2026-08-24 22:59:44.680752	\N
91	طلال يوسف	772896197	\N	القرية - المركز - ذمار	معلم	عادي	48d64cd5e88f876aafedbc66a5e482b4$1c061370d44796f8a36f4635eac0bb8e2d53eb0769ca17932799a8b1186589e9	2026-08-24 22:59:44.680752	\N
92	فهد خالد	776126698	\N	المنطقة - المدينة - عدن	مزارع	VIP	14ac38cdfb30a53e1ba847c4936c1175$5baae6764b09e1b4c99cc429108639d610edb192307074fcc6934aa7b0717a2e	2026-08-24 22:59:44.680752	\N
93	فهد يوسف	770469905	\N	القرية - المدينة - إب	موظف حكومي	عادي	72d070089f2791236b5637cc9baeff93$68523bb495e362b9131c41a7dda24bf197b78ed58945134f24f7c1b985ccb268	2026-08-24 22:59:44.680752	\N
94	طلال يوسف	774740635	776136743	الحي - الجنوبية - ذمار	مقاول	عادي	deb3d1177f6c5b96065ee42b758e91dc$9dfc1df0ee7fa1db824900e9b171da2b194944a7f35bc6333559d0fc8b327ba1	2026-08-24 22:59:44.680752	\N
95	بلال علي	776868410	\N	الشارع - الجنوبية - حضرموت	مقاول	عادي	3c82b6fd5213285e2d4e5dd4b2c65b01$d6d1bfe8fbcf812b3b1fa2c4fbd7bc3533395981ce17ef30878021ce07f2f14e	2026-08-24 22:59:44.680752	\N
96	وليد محمد	779412783	\N	الحارة - الشمالية - عدن	مهندس	كفالة	b033b340dd6aef890c787f9c08e9e6ab$8b2ee83aee386a260d1f3bc173fe95b7b627d3f015ba02ede6029b90687556ed	2026-08-24 22:59:44.680752	\N
97	عمر علي	775924175	777604248	القرية - المدينة - ذمار	سائق	عادي	956650826b185e83d8d37bbb25f7a5f0$b595212d7f1095478be09ece8a01c7068889000a0554f937bc45c27402e5624c	2026-08-24 22:59:44.680752	\N
98	علي علي	777831816	\N	الحارة - الغربية - صنعاء	موظف حكومي	كفالة	355127e4f65226c29b6e5590febaa6f0$a4519a9c3f016b8eaa062b2343d7c6bea34cae25352d5fd937d7de8d0bcbaace	2026-08-24 22:59:44.680752	\N
99	زياد محمد	774441867	\N	المنطقة - المركز - عدن	تاجر	كفالة	62928832483b5bb15735e271abb57193$df7666653338226ff35a3925b76859536bd2807a47fa4f5d3712e2d3b1c241c0	2026-08-24 22:59:44.680752	\N
100	عمر خالد	772816600	\N	القرية - المدينة - صنعاء	طبيب	عادي	ecdb89007f6598ded981684441f83ba5$16388ad79a1ff24b2567764a87b5f70597ba49a225a9bba91364cda11c95b49d	2026-08-24 22:59:44.680752	\N
30	أحمد حسن	773280107	\N	الشارع - المدينة - ذمار	مقاول	كفالة	0633baab54dbda72f81593b4ee160c94$a6b52206fe07b07400e25ac99f0d1cf4f511553c2096098acb73bb356725ad1c	2026-08-24 22:59:44.680752	2026-08-27 01:21:54.467972
\.


--
-- Data for Name: payroll_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payroll_records (id, employee_id, month, year, basic_salary, total_allowances, total_deductions, loan_deduction, net_salary, payment_status, payment_date, created_at, updated_at) FROM stdin;
1	1	8	2026	0.00	0.00	0.00	0.00	0.00	معلق	\N	2026-08-22 04:44:21.227935	\N
2	5	7	2026	111926.00	24252.00	3417.00	3664.00	129097.00	معلق	\N	2026-08-24 22:59:44.680752	\N
3	6	7	2026	236904.00	17802.00	4112.00	4561.00	246033.00	معلق	2026-08-23 22:59:48.891151	2026-08-24 22:59:44.680752	\N
4	7	7	2026	221906.00	20638.00	5307.00	8108.00	229129.00	معلق	2026-08-13 22:59:48.891186	2026-08-24 22:59:44.680752	\N
5	8	7	2026	227081.00	10060.00	2105.00	12563.00	222473.00	مسلم	2026-08-20 22:59:48.891218	2026-08-24 22:59:44.680752	\N
6	9	7	2026	119646.00	5478.00	1914.00	11735.00	111475.00	معلق	\N	2026-08-24 22:59:44.680752	\N
7	10	7	2026	147433.00	11996.00	7414.00	10732.00	141283.00	مسلم	2026-08-13 22:59:48.891273	2026-08-24 22:59:44.680752	\N
8	11	7	2026	127427.00	15899.00	9721.00	3487.00	130118.00	مسلم	2026-08-12 22:59:48.891298	2026-08-24 22:59:44.680752	\N
9	12	7	2026	248985.00	8093.00	2507.00	16689.00	237882.00	مسلم	2026-08-13 22:59:48.891324	2026-08-24 22:59:44.680752	\N
10	13	7	2026	128636.00	18620.00	7390.00	6073.00	133793.00	مسلم	2026-08-22 22:59:48.891349	2026-08-24 22:59:44.680752	\N
11	14	7	2026	212050.00	20381.00	8099.00	3801.00	220531.00	مسلم	\N	2026-08-24 22:59:44.680752	\N
12	15	7	2026	163636.00	1539.00	8165.00	7086.00	149924.00	مسلم	\N	2026-08-24 22:59:44.680752	\N
13	16	7	2026	123808.00	11170.00	5860.00	15925.00	113193.00	مسلم	2026-08-19 22:59:48.891431	2026-08-24 22:59:44.680752	\N
14	17	7	2026	146387.00	27832.00	7354.00	18417.00	148448.00	مسلم	2026-08-18 22:59:48.89146	2026-08-24 22:59:44.680752	\N
15	18	7	2026	100303.00	12492.00	3655.00	2984.00	106156.00	مسلم	2026-08-20 22:59:48.891486	2026-08-24 22:59:44.680752	\N
16	19	7	2026	168836.00	21554.00	5637.00	5867.00	178886.00	مسلم	\N	2026-08-24 22:59:44.680752	\N
17	5	8	2026	111926.00	20905.00	10823.00	16641.92	105366.08	معلق	\N	2026-08-25 05:18:35.237844	\N
18	6	8	2026	236904.00	23986.00	0.00	45988.00	214902.00	معلق	\N	2026-08-25 05:18:35.237844	\N
19	8	8	2026	227081.00	7952.00	0.00	0.00	235033.00	معلق	\N	2026-08-25 05:18:35.237844	\N
20	10	8	2026	147433.00	14497.00	0.00	0.00	161930.00	معلق	\N	2026-08-25 05:18:35.237844	\N
21	11	8	2026	127427.00	16867.00	29265.00	31260.25	83768.75	معلق	\N	2026-08-25 05:18:35.237844	\N
23	13	8	2026	128636.00	25144.00	0.00	0.00	153780.00	معلق	\N	2026-08-25 05:18:35.237844	\N
24	14	8	2026	212050.00	0.00	41353.00	16732.38	153964.62	معلق	\N	2026-08-25 05:18:35.237844	\N
25	15	8	2026	163636.00	0.00	0.00	0.00	163636.00	معلق	\N	2026-08-25 05:18:35.237844	\N
26	16	8	2026	123808.00	0.00	0.00	0.00	123808.00	معلق	\N	2026-08-25 05:18:35.237844	\N
27	18	8	2026	100303.00	0.00	0.00	0.00	100303.00	معلق	\N	2026-08-25 05:18:35.237844	\N
28	19	8	2026	168836.00	28583.00	0.00	0.00	197419.00	معلق	\N	2026-08-25 05:18:35.237844	\N
29	20	8	2026	118026.00	0.00	0.00	0.00	118026.00	معلق	\N	2026-08-25 05:18:35.237844	\N
30	22	8	2026	97649.00	0.00	0.00	0.00	97649.00	معلق	\N	2026-08-25 05:18:35.237844	\N
31	23	8	2026	117980.00	0.00	0.00	0.00	117980.00	معلق	\N	2026-08-25 05:18:35.237844	\N
32	24	8	2026	169821.00	0.00	0.00	0.00	169821.00	معلق	\N	2026-08-25 05:18:35.237844	\N
33	25	8	2026	167367.00	0.00	0.00	0.00	167367.00	معلق	\N	2026-08-25 05:18:35.237844	\N
34	27	8	2026	197153.00	0.00	0.00	0.00	197153.00	معلق	\N	2026-08-25 05:18:35.237844	\N
35	28	8	2026	173838.00	0.00	0.00	0.00	173838.00	معلق	\N	2026-08-25 05:18:35.237844	\N
36	29	8	2026	213489.00	0.00	0.00	0.00	213489.00	معلق	\N	2026-08-25 05:18:35.237844	\N
37	30	8	2026	129386.00	0.00	0.00	0.00	129386.00	معلق	\N	2026-08-25 05:18:35.237844	\N
38	31	8	2026	229136.00	0.00	0.00	0.00	229136.00	معلق	\N	2026-08-25 05:18:35.237844	\N
39	34	8	2026	170565.00	0.00	0.00	0.00	170565.00	معلق	\N	2026-08-25 05:18:35.237844	\N
47	12	9	2026	248985.00	0.00	0.00	21407.22	227577.78	مسلم	2026-09-02 03:53:25.745742	2026-09-01 05:23:37.761486	2026-09-02 03:53:25.745263
72	12	6	2026	248985.00	0.00	0.00	21407.22	227577.78	مسلم	2026-09-01 05:28:24.285618	2026-09-01 05:24:03.566655	2026-09-01 05:28:24.284535
22	12	8	2026	248985.00	0.00	0.00	21407.22	227577.78	مسلم	2026-08-29 03:34:10.536918	2026-08-25 05:18:35.237844	2026-08-29 03:34:10.535376
69	6	6	2026	236904.00	0.00	0.00	45988.00	190916.00	مسلم	2026-09-01 05:29:53.253642	2026-09-01 05:24:03.566655	2026-09-01 05:29:53.252661
40	32	8	2026	91759.00	0.00	0.00	0.00	91759.00	مسلم	2026-08-29 03:34:14.654449	2026-08-25 05:18:35.237844	2026-08-29 03:34:14.653151
41	1	9	2026	0.00	0.00	0.00	0.00	0.00	معلق	\N	2026-09-01 05:23:37.761486	\N
42	10	9	2026	147433.00	0.00	0.00	0.00	147433.00	معلق	\N	2026-09-01 05:23:37.761486	\N
43	5	9	2026	111926.00	0.00	0.00	16641.92	95284.08	معلق	\N	2026-09-01 05:23:37.761486	\N
45	8	9	2026	227081.00	0.00	0.00	0.00	227081.00	معلق	\N	2026-09-01 05:23:37.761486	\N
46	11	9	2026	127427.00	0.00	0.00	31260.25	96166.75	معلق	\N	2026-09-01 05:23:37.761486	\N
48	13	9	2026	128636.00	0.00	0.00	0.00	128636.00	معلق	\N	2026-09-01 05:23:37.761486	\N
49	14	9	2026	212050.00	0.00	0.00	16732.38	195317.62	معلق	\N	2026-09-01 05:23:37.761486	\N
50	15	9	2026	163636.00	0.00	0.00	0.00	163636.00	معلق	\N	2026-09-01 05:23:37.761486	\N
51	16	9	2026	123808.00	0.00	0.00	0.00	123808.00	معلق	\N	2026-09-01 05:23:37.761486	\N
52	18	9	2026	100303.00	0.00	0.00	0.00	100303.00	معلق	\N	2026-09-01 05:23:37.761486	\N
53	19	9	2026	168836.00	0.00	0.00	0.00	168836.00	معلق	\N	2026-09-01 05:23:37.761486	\N
54	20	9	2026	118026.00	0.00	0.00	0.00	118026.00	معلق	\N	2026-09-01 05:23:37.761486	\N
55	22	9	2026	97649.00	0.00	0.00	0.00	97649.00	معلق	\N	2026-09-01 05:23:37.761486	\N
56	23	9	2026	117980.00	0.00	0.00	0.00	117980.00	معلق	\N	2026-09-01 05:23:37.761486	\N
57	24	9	2026	169821.00	0.00	0.00	0.00	169821.00	معلق	\N	2026-09-01 05:23:37.761486	\N
58	25	9	2026	167367.00	0.00	0.00	0.00	167367.00	معلق	\N	2026-09-01 05:23:37.761486	\N
59	27	9	2026	197153.00	0.00	0.00	0.00	197153.00	معلق	\N	2026-09-01 05:23:37.761486	\N
60	28	9	2026	173838.00	0.00	0.00	0.00	173838.00	معلق	\N	2026-09-01 05:23:37.761486	\N
61	29	9	2026	213489.00	0.00	0.00	0.00	213489.00	معلق	\N	2026-09-01 05:23:37.761486	\N
62	30	9	2026	129386.00	0.00	0.00	0.00	129386.00	معلق	\N	2026-09-01 05:23:37.761486	\N
63	31	9	2026	229136.00	0.00	0.00	0.00	229136.00	معلق	\N	2026-09-01 05:23:37.761486	\N
64	34	9	2026	170565.00	0.00	0.00	0.00	170565.00	معلق	\N	2026-09-01 05:23:37.761486	\N
65	32	9	2026	91759.00	0.00	0.00	0.00	91759.00	معلق	\N	2026-09-01 05:23:37.761486	\N
66	1	6	2026	0.00	0.00	0.00	0.00	0.00	معلق	\N	2026-09-01 05:24:03.566655	\N
67	10	6	2026	147433.00	0.00	0.00	0.00	147433.00	معلق	\N	2026-09-01 05:24:03.566655	\N
68	5	6	2026	111926.00	0.00	0.00	16641.92	95284.08	معلق	\N	2026-09-01 05:24:03.566655	\N
70	8	6	2026	227081.00	0.00	0.00	0.00	227081.00	معلق	\N	2026-09-01 05:24:03.566655	\N
71	11	6	2026	127427.00	0.00	0.00	31260.25	96166.75	معلق	\N	2026-09-01 05:24:03.566655	\N
73	13	6	2026	128636.00	0.00	0.00	0.00	128636.00	معلق	\N	2026-09-01 05:24:03.566655	\N
74	14	6	2026	212050.00	0.00	0.00	16732.38	195317.62	معلق	\N	2026-09-01 05:24:03.566655	\N
75	15	6	2026	163636.00	0.00	0.00	0.00	163636.00	معلق	\N	2026-09-01 05:24:03.566655	\N
76	16	6	2026	123808.00	0.00	0.00	0.00	123808.00	معلق	\N	2026-09-01 05:24:03.566655	\N
77	18	6	2026	100303.00	0.00	0.00	0.00	100303.00	معلق	\N	2026-09-01 05:24:03.566655	\N
78	19	6	2026	168836.00	0.00	0.00	0.00	168836.00	معلق	\N	2026-09-01 05:24:03.566655	\N
79	20	6	2026	118026.00	0.00	0.00	0.00	118026.00	معلق	\N	2026-09-01 05:24:03.566655	\N
44	6	9	2026	236904.00	0.00	0.00	45988.00	190916.00	مسلم	2026-09-01 05:31:16.060731	2026-09-01 05:23:37.761486	2026-09-01 05:31:16.05974
80	22	6	2026	97649.00	0.00	0.00	0.00	97649.00	معلق	\N	2026-09-01 05:24:03.566655	\N
81	23	6	2026	117980.00	0.00	0.00	0.00	117980.00	معلق	\N	2026-09-01 05:24:03.566655	\N
82	24	6	2026	169821.00	0.00	0.00	0.00	169821.00	معلق	\N	2026-09-01 05:24:03.566655	\N
83	25	6	2026	167367.00	0.00	0.00	0.00	167367.00	معلق	\N	2026-09-01 05:24:03.566655	\N
84	27	6	2026	197153.00	0.00	0.00	0.00	197153.00	معلق	\N	2026-09-01 05:24:03.566655	\N
85	28	6	2026	173838.00	0.00	0.00	0.00	173838.00	معلق	\N	2026-09-01 05:24:03.566655	\N
86	29	6	2026	213489.00	0.00	0.00	0.00	213489.00	معلق	\N	2026-09-01 05:24:03.566655	\N
87	30	6	2026	129386.00	0.00	0.00	0.00	129386.00	معلق	\N	2026-09-01 05:24:03.566655	\N
88	31	6	2026	229136.00	0.00	0.00	0.00	229136.00	معلق	\N	2026-09-01 05:24:03.566655	\N
89	34	6	2026	170565.00	0.00	0.00	0.00	170565.00	معلق	\N	2026-09-01 05:24:03.566655	\N
90	32	6	2026	91759.00	0.00	0.00	0.00	91759.00	معلق	\N	2026-09-01 05:24:03.566655	\N
91	1	10	2026	0.00	0.00	0.00	0.00	0.00	معلق	\N	2026-09-02 04:05:04.46345	\N
92	10	10	2026	147433.00	0.00	0.00	0.00	147433.00	معلق	\N	2026-09-02 04:05:04.46345	\N
94	6	10	2026	236904.00	0.00	0.00	45988.00	190916.00	معلق	\N	2026-09-02 04:05:04.46345	\N
95	8	10	2026	227081.00	0.00	0.00	0.00	227081.00	معلق	\N	2026-09-02 04:05:04.46345	\N
96	11	10	2026	127427.00	0.00	0.00	31260.25	96166.75	معلق	\N	2026-09-02 04:05:04.46345	\N
97	12	10	2026	248985.00	0.00	0.00	21407.22	227577.78	معلق	\N	2026-09-02 04:05:04.46345	\N
98	13	10	2026	128636.00	0.00	0.00	0.00	128636.00	معلق	\N	2026-09-02 04:05:04.46345	\N
99	14	10	2026	212050.00	0.00	0.00	16732.38	195317.62	معلق	\N	2026-09-02 04:05:04.46345	\N
100	15	10	2026	163636.00	0.00	0.00	0.00	163636.00	معلق	\N	2026-09-02 04:05:04.46345	\N
101	16	10	2026	123808.00	0.00	0.00	0.00	123808.00	معلق	\N	2026-09-02 04:05:04.46345	\N
102	18	10	2026	100303.00	0.00	0.00	0.00	100303.00	معلق	\N	2026-09-02 04:05:04.46345	\N
103	19	10	2026	168836.00	0.00	0.00	0.00	168836.00	معلق	\N	2026-09-02 04:05:04.46345	\N
104	20	10	2026	118026.00	0.00	0.00	0.00	118026.00	معلق	\N	2026-09-02 04:05:04.46345	\N
105	22	10	2026	97649.00	0.00	0.00	0.00	97649.00	معلق	\N	2026-09-02 04:05:04.46345	\N
106	23	10	2026	117980.00	0.00	0.00	0.00	117980.00	معلق	\N	2026-09-02 04:05:04.46345	\N
107	24	10	2026	169821.00	0.00	0.00	0.00	169821.00	معلق	\N	2026-09-02 04:05:04.46345	\N
108	25	10	2026	167367.00	0.00	0.00	0.00	167367.00	معلق	\N	2026-09-02 04:05:04.46345	\N
109	27	10	2026	197153.00	0.00	0.00	0.00	197153.00	معلق	\N	2026-09-02 04:05:04.46345	\N
110	28	10	2026	173838.00	0.00	0.00	0.00	173838.00	معلق	\N	2026-09-02 04:05:04.46345	\N
111	29	10	2026	213489.00	0.00	0.00	0.00	213489.00	معلق	\N	2026-09-02 04:05:04.46345	\N
112	30	10	2026	129386.00	0.00	0.00	0.00	129386.00	معلق	\N	2026-09-02 04:05:04.46345	\N
113	31	10	2026	229136.00	0.00	0.00	0.00	229136.00	معلق	\N	2026-09-02 04:05:04.46345	\N
114	34	10	2026	170565.00	0.00	0.00	0.00	170565.00	معلق	\N	2026-09-02 04:05:04.46345	\N
115	32	10	2026	91759.00	0.00	0.00	0.00	91759.00	معلق	\N	2026-09-02 04:05:04.46345	\N
93	5	10	2026	111926.00	0.00	0.00	36641.92	75284.08	مسلم	2026-09-02 04:05:23.974488	2026-09-02 04:05:04.46345	2026-09-02 04:05:23.973673
\.


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.permissions (id, module_name, permission_key) FROM stdin;
79	لوحة التحكم	module_0
80	لوحة المحاسب	module_1
81	التهيئة الأكاديمية	module_2
82	إدارة الطلاب	module_3
83	أولياء الأمور	module_4
84	وثائق الطلاب	module_5
85	توزيع الطلاب	module_6
86	رسوم الطلاب	module_7
87	سندات القبض	module_8
88	كشف حساب طالب	module_9
89	الموظفين والمعلمين	module_10
90	سندات الصرف	module_11
91	البدلات والخصومات	module_12
92	السلف المالية	module_13
93	كشف الرواتب	module_14
94	كشف حساب موظف	module_15
95	رصد الدرجات	module_16
96	الشهادات والأوائل	module_17
97	الحضور والغياب	module_18
98	الواجبات المنزلية	module_19
99	المتابعة السلوكية	module_20
100	الجداول الدراسية	module_21
101	المستخدمين	module_22
102	الصلاحيات	module_23
103	الإشعارات	module_24
104	التقارير	module_25
105	الإعدادات	module_26
\.


--
-- Data for Name: print_archive; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.print_archive (id, document_type, document_number, related_record_id, printed_by, printed_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: receipts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.receipts (id, receipt_number, student_id, installment_id, payment_target, amount_paid, payment_date, payment_method, reference_number, notes, created_by_user_id, status, cancellation_reason, cancelled_at, created_at, updated_at) FROM stdin;
1	RCV-01-00001	1	\N	current_fee	99936.00	2026-08-19 22:59:48.833501	تحويل بنكي	\N		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
2	RCV-01-00002	2	\N	previous_debt	85040.00	2026-05-04 22:59:48.833597	كريمي/حاسب	\N	دفعة مقدمة	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
3	RCV-01-00003	2	\N	previous_debt	92833.00	2026-06-13 22:59:48.833635	تحويل بنكي	REF-88931	دفعة مقدمة	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
4	RCV-01-00004	3	\N	current_fee	57322.00	2026-08-09 22:59:48.833672	نقداً	\N	سداد قسط	1	ملغى	خطأ في المبلغ	\N	2026-08-24 22:59:44.680752	\N
5	RCV-01-00005	4	\N	previous_debt	31319.00	2026-08-12 22:59:48.833703	تحويل بنكي	REF-26173		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
6	RCV-01-00006	4	\N	current_fee	78696.00	2026-05-28 22:59:48.833732	كريمي/حاسب	\N	تسوية	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
7	RCV-01-00007	5	\N	previous_debt	99704.00	2026-06-18 22:59:48.833759	كريمي/حاسب	\N	تسوية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
8	RCV-01-00008	5	\N	previous_debt	31982.00	2026-08-08 22:59:48.833785	نقداً	REF-66499		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
9	RCV-01-00009	5	\N	current_fee	31806.00	2026-06-03 22:59:48.833812	تحويل بنكي	\N		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
10	RCV-01-00010	6	\N	current_fee	26816.00	2026-07-05 22:59:48.833839	نقداً	\N	تسوية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
11	RCV-01-00011	7	\N	current_fee	86331.00	2026-06-22 22:59:48.833864	تحويل بنكي	\N	دفعة مقدمة	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
12	RCV-01-00012	7	\N	previous_debt	23047.00	2026-05-28 22:59:48.833888	تحويل بنكي	\N	تسوية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
13	RCV-01-00013	8	\N	current_fee	55616.00	2026-06-22 22:59:48.833914	نقداً	\N	دفعة مقدمة	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
14	RCV-01-00014	9	\N	previous_debt	54348.00	2026-07-15 22:59:48.833941	نقداً	\N		1	نشط	خطأ في المبلغ	\N	2026-08-24 22:59:44.680752	\N
15	RCV-01-00015	9	\N	current_fee	60557.00	2026-08-10 22:59:48.833967	كريمي/حاسب	\N	دفعة مقدمة	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
16	RCV-01-00016	9	\N	previous_debt	49954.00	2026-06-04 22:59:48.833994	كريمي/حاسب	REF-69280		1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
17	RCV-01-00017	10	\N	previous_debt	95846.00	2026-07-29 22:59:48.834027	تحويل بنكي	\N	دفعة مقدمة	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
18	RCV-01-00018	10	\N	previous_debt	92478.00	2026-07-13 22:59:48.834052	نقداً	REF-87500	تسوية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
19	RCV-01-00019	10	\N	current_fee	63651.00	2026-07-14 22:59:48.834078	تحويل بنكي	\N	دفعة مقدمة	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
20	RCV-01-00020	11	\N	current_fee	50589.00	2026-06-06 22:59:48.834107	كريمي/حاسب	\N	دفعة مقدمة	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
21	RCV-01-00021	12	\N	previous_debt	59466.00	2026-08-22 22:59:48.834134	كريمي/حاسب	REF-68567	سداد قسط	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
22	RCV-01-00022	12	\N	previous_debt	49138.00	2026-05-09 22:59:48.834162	نقداً	REF-93696	تسوية	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
23	RCV-01-00023	13	\N	current_fee	67965.00	2026-06-03 22:59:48.834189	كريمي/حاسب	\N		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
24	RCV-01-00024	13	\N	current_fee	84005.00	2026-05-27 22:59:48.834215	كريمي/حاسب	REF-43652	سداد قسط	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
25	RCV-01-00025	13	\N	previous_debt	93174.00	2026-05-26 22:59:48.834241	تحويل بنكي	\N	دفعة مقدمة	1	نشط	خطأ في المبلغ	\N	2026-08-24 22:59:44.680752	\N
26	RCV-01-00026	14	\N	current_fee	80155.00	2026-05-02 22:59:48.834266	تحويل بنكي	\N	تسوية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
27	RCV-01-00027	15	\N	previous_debt	25373.00	2026-06-15 22:59:48.834295	كريمي/حاسب	\N		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
28	RCV-01-00028	15	\N	previous_debt	93971.00	2026-07-14 22:59:48.834321	كريمي/حاسب	REF-69164	تسوية	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
29	RCV-01-00029	15	\N	previous_debt	57098.00	2026-04-26 22:59:48.834347	تحويل بنكي	\N		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
30	RCV-01-00030	16	\N	current_fee	95994.00	2026-06-19 22:59:48.834373	تحويل بنكي	REF-13677	دفعة مقدمة	1	ملغى	خطأ في المبلغ	\N	2026-08-24 22:59:44.680752	\N
31	RCV-01-00031	16	\N	current_fee	54578.00	2026-05-30 22:59:48.8344	تحويل بنكي	\N		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
32	RCV-01-00032	16	\N	previous_debt	89640.00	2026-07-19 22:59:48.834426	نقداً	\N	دفعة مقدمة	1	نشط	خطأ في المبلغ	\N	2026-08-24 22:59:44.680752	\N
33	RCV-01-00033	17	\N	previous_debt	91967.00	2026-04-29 22:59:48.834451	تحويل بنكي	REF-90496	تسوية	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
34	RCV-01-00034	17	\N	previous_debt	84765.00	2026-08-15 22:59:48.834478	تحويل بنكي	\N		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
35	RCV-01-00035	17	\N	current_fee	23926.00	2026-05-24 22:59:48.834504	كريمي/حاسب	\N		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
36	RCV-01-00036	18	\N	current_fee	68000.00	2026-08-11 22:59:48.834529	نقداً	REF-78332		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
37	RCV-01-00037	18	\N	current_fee	20602.00	2026-07-18 22:59:48.834555	تحويل بنكي	REF-85827	سداد قسط	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
38	RCV-01-00038	19	\N	previous_debt	38428.00	2026-07-17 22:59:48.834581	كريمي/حاسب	\N	تسوية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
39	RCV-01-00039	19	\N	current_fee	72358.00	2026-06-22 22:59:48.834614	تحويل بنكي	\N	تسوية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
40	RCV-01-00040	19	\N	current_fee	53746.00	2026-08-22 22:59:48.834639	نقداً	\N	تسوية	1	نشط	خطأ في المبلغ	\N	2026-08-24 22:59:44.680752	\N
41	RCV-01-00041	20	\N	previous_debt	40790.00	2026-05-07 22:59:48.834667	نقداً	REF-55860	دفعة مقدمة	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
42	RCV-01-00042	20	\N	previous_debt	43663.00	2026-08-19 22:59:48.834692	نقداً	REF-81304	تسوية	1	نشط	خطأ في المبلغ	\N	2026-08-24 22:59:44.680752	\N
43	RCV-01-00043	21	\N	previous_debt	74124.00	2026-05-02 22:59:48.834719	نقداً	\N	سداد قسط	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
44	RCV-01-00044	22	\N	previous_debt	57916.00	2026-05-14 22:59:48.834744	كريمي/حاسب	REF-94176	تسوية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
45	RCV-01-00045	22	\N	current_fee	29127.00	2026-07-30 22:59:48.834769	كريمي/حاسب	\N		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
46	RCV-01-00046	22	\N	current_fee	57242.00	2026-06-03 22:59:48.834794	كريمي/حاسب	REF-52616	دفعة مقدمة	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
47	RCV-01-00047	23	\N	current_fee	64747.00	2026-05-21 22:59:48.834819	تحويل بنكي	REF-95381	تسوية	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
48	RCV-01-00048	23	\N	previous_debt	59399.00	2026-08-02 22:59:48.834846	تحويل بنكي	REF-43344	سداد قسط	1	نشط	خطأ في المبلغ	\N	2026-08-24 22:59:44.680752	\N
49	RCV-01-00049	24	\N	previous_debt	78646.00	2026-06-09 22:59:48.834874	كريمي/حاسب	\N	تسوية	1	نشط	خطأ في المبلغ	\N	2026-08-24 22:59:44.680752	\N
50	RCV-01-00050	24	\N	current_fee	85239.00	2026-08-14 22:59:48.834899	نقداً	\N		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
51	RCV-01-00051	25	\N	current_fee	74044.00	2026-05-28 22:59:48.834924	نقداً	REF-81586	دفعة مقدمة	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
52	RCV-01-00052	26	\N	current_fee	44211.00	2026-05-26 22:59:48.834949	نقداً	\N		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
53	RCV-01-00053	26	\N	current_fee	83470.00	2026-06-28 22:59:48.834973	كريمي/حاسب	REF-45388	دفعة مقدمة	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
55	RCV-01-00055	27	\N	current_fee	57391.00	2026-07-08 22:59:48.835023	تحويل بنكي	REF-75441		1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
56	RCV-01-00056	27	\N	previous_debt	50332.00	2026-08-10 22:59:48.835048	كريمي/حاسب	REF-75152	دفعة مقدمة	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
57	RCV-01-00057	28	\N	current_fee	55912.00	2026-06-11 22:59:48.835076	تحويل بنكي	\N		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
58	RCV-01-00058	28	\N	current_fee	35814.00	2026-06-09 22:59:48.8351	تحويل بنكي	\N	سداد قسط	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
59	RCV-01-00059	29	\N	previous_debt	76290.00	2026-06-08 22:59:48.835127	تحويل بنكي	REF-83339	دفعة مقدمة	1	نشط	خطأ في المبلغ	\N	2026-08-24 22:59:44.680752	\N
60	RCV-01-00060	29	\N	current_fee	61038.00	2026-08-15 22:59:48.835153	كريمي/حاسب	REF-36815	دفعة مقدمة	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
61	RCV-01-00061	30	\N	current_fee	63689.00	2026-07-22 22:59:48.835178	نقداً	REF-90662	تسوية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
62	RCV-01-00062	30	\N	previous_debt	78994.00	2026-06-30 22:59:48.835202	تحويل بنكي	REF-54157	دفعة مقدمة	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
63	RCV-01-00063	30	\N	previous_debt	99916.00	2026-05-03 22:59:48.835228	نقداً	REF-44384	تسوية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
64	RCV-01-00064	31	\N	previous_debt	54180.00	2026-05-06 22:59:48.835253	كريمي/حاسب	REF-25212		1	نشط	خطأ في المبلغ	\N	2026-08-24 22:59:44.680752	\N
65	RCV-01-00065	32	\N	current_fee	76102.00	2026-07-13 22:59:48.83528	كريمي/حاسب	\N	دفعة مقدمة	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
66	RCV-01-00066	32	\N	current_fee	51277.00	2026-05-24 22:59:48.835305	تحويل بنكي	\N		1	نشط	خطأ في المبلغ	\N	2026-08-24 22:59:44.680752	\N
67	RCV-01-00067	33	\N	previous_debt	77609.00	2026-05-27 22:59:48.835332	نقداً	\N	تسوية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
68	RCV-01-00068	33	\N	previous_debt	74431.00	2026-08-20 22:59:48.835356	تحويل بنكي	REF-74664	تسوية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
69	RCV-01-00069	33	\N	previous_debt	72952.00	2026-05-01 22:59:48.835381	نقداً	REF-85888	سداد قسط	1	ملغى	خطأ في المبلغ	\N	2026-08-24 22:59:44.680752	\N
70	RCV-01-00070	34	\N	current_fee	47948.00	2026-06-22 22:59:48.835407	نقداً	REF-14295	سداد قسط	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
71	RCV-01-00071	34	\N	current_fee	87371.00	2026-07-25 22:59:48.835431	نقداً	\N	تسوية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
72	RCV-01-00072	34	\N	previous_debt	96779.00	2026-05-06 22:59:48.835456	تحويل بنكي	REF-86668	دفعة مقدمة	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
73	RCV-01-00073	35	\N	current_fee	32478.00	2026-07-19 22:59:48.83548	تحويل بنكي	REF-18860	تسوية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
74	RCV-01-00074	36	\N	previous_debt	72630.00	2026-06-18 22:59:48.835506	نقداً	\N	دفعة مقدمة	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
75	RCV-01-00075	36	\N	current_fee	49617.00	2026-07-21 22:59:48.83553	تحويل بنكي	\N	تسوية	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
76	RCV-01-00076	36	\N	current_fee	23902.00	2026-06-12 22:59:48.835554	نقداً	\N	سداد قسط	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
77	RCV-01-00077	37	\N	previous_debt	32506.00	2026-06-09 22:59:48.835579	تحويل بنكي	REF-18542	دفعة مقدمة	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
78	RCV-01-00078	37	\N	previous_debt	66459.00	2026-07-04 22:59:48.835603	نقداً	\N		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
79	RCV-01-00079	38	\N	previous_debt	32041.00	2026-05-11 22:59:48.835629	تحويل بنكي	\N	دفعة مقدمة	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
80	RCV-01-00080	38	\N	previous_debt	92364.00	2026-05-08 22:59:48.835652	كريمي/حاسب	REF-65667	دفعة مقدمة	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
81	RCV-01-00081	38	\N	previous_debt	51092.00	2026-07-22 22:59:48.835677	نقداً	REF-13202		1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
82	RCV-01-00082	39	\N	previous_debt	57932.00	2026-07-01 22:59:48.835701	تحويل بنكي	REF-77873	سداد قسط	1	نشط	خطأ في المبلغ	\N	2026-08-24 22:59:44.680752	\N
83	RCV-01-00083	40	\N	current_fee	56027.00	2026-07-03 22:59:48.835728	تحويل بنكي	REF-31565	سداد قسط	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
84	RCV-01-00084	41	\N	current_fee	65392.00	2026-08-02 22:59:48.835754	نقداً	REF-97154	سداد قسط	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
85	RCV-01-00085	41	\N	previous_debt	84298.00	2026-05-09 22:59:48.835778	كريمي/حاسب	\N	دفعة مقدمة	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
86	RCV-01-00086	41	\N	current_fee	96267.00	2026-08-04 22:59:48.835802	تحويل بنكي	REF-63025	دفعة مقدمة	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
87	RCV-01-00087	42	\N	current_fee	45211.00	2026-06-03 22:59:48.835827	كريمي/حاسب	\N	سداد قسط	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
88	RCV-01-00088	43	\N	current_fee	83463.00	2026-05-19 22:59:48.835852	نقداً	REF-76100	سداد قسط	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
89	RCV-01-00089	43	\N	previous_debt	35315.00	2026-05-02 22:59:48.835878	كريمي/حاسب	REF-22970	دفعة مقدمة	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
90	RCV-01-00090	43	\N	current_fee	42290.00	2026-05-12 22:59:48.835901	كريمي/حاسب	\N		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
91	RCV-01-00091	44	\N	previous_debt	79127.00	2026-06-23 22:59:48.835927	نقداً	REF-72003	سداد قسط	1	نشط	خطأ في المبلغ	\N	2026-08-24 22:59:44.680752	\N
93	RCV-01-00093	45	\N	previous_debt	51754.00	2026-05-16 22:59:48.835977	كريمي/حاسب	REF-79968	دفعة مقدمة	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
94	RCV-01-00094	46	\N	current_fee	43544.00	2026-07-01 22:59:48.836001	تحويل بنكي	REF-41050	سداد قسط	1	نشط	خطأ في المبلغ	\N	2026-08-24 22:59:44.680752	\N
95	RCV-01-00095	47	\N	previous_debt	46698.00	2026-06-18 22:59:48.836026	كريمي/حاسب	REF-32658	تسوية	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
96	RCV-01-00096	48	\N	previous_debt	29370.00	2026-08-02 22:59:48.83605	نقداً	\N	دفعة مقدمة	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
97	RCV-01-00097	49	\N	previous_debt	78033.00	2026-07-21 22:59:48.836075	نقداً	REF-47086	سداد قسط	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
98	RCV-01-00098	50	\N	previous_debt	35670.00	2026-08-13 22:59:48.836101	كريمي/حاسب	REF-76866	سداد قسط	1	ملغى	خطأ في المبلغ	\N	2026-08-24 22:59:44.680752	\N
99	RCV-01-00099	51	\N	current_fee	56761.00	2026-06-27 22:59:48.836127	نقداً	\N	دفعة مقدمة	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
100	RCV-01-00100	51	\N	previous_debt	79498.00	2026-08-03 22:59:48.836151	نقداً	\N	سداد قسط	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
101	RCV-01-00101	52	\N	previous_debt	37632.00	2026-08-14 22:59:48.836176	نقداً	REF-98683		1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
102	RCV-01-00102	52	\N	previous_debt	71487.00	2026-07-18 22:59:48.8362	تحويل بنكي	\N	سداد قسط	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
103	RCV-01-00103	53	\N	previous_debt	35000.00	2026-06-05 22:59:48.836224	كريمي/حاسب	REF-32777	تسوية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
104	RCV-01-00104	54	\N	current_fee	68949.00	2026-08-09 22:59:48.836249	تحويل بنكي	REF-71615	سداد قسط	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
92	RCV-01-00092	44	\N	previous_debt	25365.00	2026-04-30 22:59:48.835952	نقداً	REF-92227	سداد قسط	1	ملغى	ss	2026-08-25 04:12:48.748422	2026-08-24 22:59:44.680752	2026-08-25 04:12:48.74738
105	RCV-01-00105	54	\N	previous_debt	42808.00	2026-05-07 22:59:48.836274	تحويل بنكي	\N	سداد قسط	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
106	RCV-01-00106	55	\N	current_fee	85399.00	2026-05-25 22:59:48.836298	نقداً	\N	سداد قسط	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
107	RCV-01-00107	55	\N	previous_debt	46884.00	2026-05-06 22:59:48.836451	كريمي/حاسب	\N		1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
108	RCV-01-00108	55	\N	current_fee	97613.00	2026-06-24 22:59:48.83649	نقداً	\N	دفعة مقدمة	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
110	RCV-01-00110	57	\N	previous_debt	61596.00	2026-08-13 22:59:48.83655	كريمي/حاسب	REF-24587	تسوية	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
111	RCV-01-00111	57	\N	previous_debt	92738.00	2026-06-09 22:59:48.836577	نقداً	REF-62570	دفعة مقدمة	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
112	RCV-01-00112	58	\N	current_fee	73839.00	2026-06-11 22:59:48.836603	كريمي/حاسب	REF-97989	دفعة مقدمة	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
113	RCV-01-00113	58	\N	previous_debt	69076.00	2026-08-15 22:59:48.836629	تحويل بنكي	REF-89859	دفعة مقدمة	1	ملغى	\N	\N	2026-08-24 22:59:44.680752	\N
114	RCV-01-00114	58	\N	current_fee	66200.00	2026-07-01 22:59:48.836654	كريمي/حاسب	REF-38167	دفعة مقدمة	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
115	RCV-01-00115	59	\N	previous_debt	70739.00	2026-08-11 22:59:48.836679	كريمي/حاسب	REF-75961	سداد قسط	1	نشط	خطأ في المبلغ	\N	2026-08-24 22:59:44.680752	\N
116	RCV-01-00116	59	\N	previous_debt	75372.00	2026-07-11 22:59:48.836704	تحويل بنكي	\N	تسوية	1	نشط	\N	\N	2026-08-24 22:59:44.680752	\N
117	RCV-01-00117	60	\N	previous_debt	84887.00	2026-07-27 22:59:48.83673	نقداً	REF-65020	سداد قسط	1	نشط	خطأ في المبلغ	\N	2026-08-24 22:59:44.680752	\N
118	RCV-01-00118	60	\N	current_fee	90523.00	2026-07-07 22:59:48.836756	كريمي/حاسب	REF-87335	تسوية	1	نشط	خطأ في المبلغ	\N	2026-08-24 22:59:44.680752	\N
109	RCV-01-00109	56	\N	previous_debt	73348.00	2026-04-30 22:59:48.836521	كريمي/حاسب	\N	دفعة مقدمة	1	ملغى		2026-08-25 04:13:10.900535	2026-08-24 22:59:44.680752	2026-08-25 04:13:10.899537
119	RCV-20260901043547	4	274	current_fee	20000.00	2026-09-01 04:36:18.912967	نقداً	\N	\N	2	نشط	\N	\N	2026-09-01 04:36:18.912967	\N
120	RCV-20260902033156	4	274	current_fee	10143.00	2026-09-02 03:32:33.215659	نقداً	\N	\N	2	نشط	\N	\N	2026-09-02 03:32:33.215659	\N
54	RCV-01-00054	26	\N	current_fee	72420.00	2026-08-23 22:59:48.834998	كريمي/حاسب	REF-85101	تسوية	1	ملغى		2026-09-05 02:02:18.184032	2026-08-24 22:59:44.680752	2026-09-05 02:02:18.182515
\.


--
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.role_permissions (role_id, permission_id, can_view, can_add, can_edit, can_delete, can_print, can_cancel) FROM stdin;
1	79	t	t	t	t	t	t
1	80	t	t	t	t	t	t
1	81	t	t	t	t	t	t
1	82	t	t	t	t	t	t
1	83	t	t	t	t	t	t
1	84	t	t	t	t	t	t
1	85	t	t	t	t	t	t
1	86	t	t	t	t	t	t
1	87	t	t	t	t	t	t
1	88	t	t	t	t	t	t
1	89	t	t	t	t	t	t
1	90	t	t	t	t	t	t
1	91	t	t	t	t	t	t
1	92	t	t	t	t	t	t
1	93	t	t	t	t	t	t
1	94	t	t	t	t	t	t
1	95	t	t	t	t	t	t
1	96	t	t	t	t	t	t
1	97	t	t	t	t	t	t
1	98	t	t	t	t	t	t
1	99	t	t	t	t	t	t
1	100	t	t	t	t	t	t
1	101	t	t	t	t	t	t
1	102	t	t	t	t	t	t
1	103	t	t	t	t	t	t
1	104	t	t	t	t	t	t
1	105	t	t	t	t	t	t
6	95	t	t	t	f	t	f
6	97	t	t	t	f	t	f
6	98	t	t	t	f	t	f
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, role_name, description, created_at, updated_at) FROM stdin;
1	مدير النظام	صلاحيات كاملة للنظام	2026-08-21 02:18:55.539882	\N
2	مدير عام	إدارة شاملة للمدرسة	2026-08-21 02:18:55.539882	\N
3	محاسب	إدارة الشؤون المالية	2026-08-21 02:18:55.539882	\N
5	أخصائي اجتماعي	متابعة الطلاب	2026-08-21 02:18:55.539882	\N
6	معلم	رصد الدرجات والحضور	2026-08-21 02:18:55.539882	\N
7	مدخل بيانات	إدخال البيانات	2026-08-21 04:38:15.703362	\N
\.


--
-- Data for Name: school_info; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.school_info (id, school_name_ar, school_name_en, principal_name, license_number, phone_primary, phone_secondary, email, address_detail, logo_url, header_footer_url, terms_and_conditions, created_at, updated_at) FROM stdin;
1	مدرسة خالد الأهلية	Al-Noor Private School	\N	\N	\N	\N	\N	\N	\N	\N	شروط وأحكام المدرسة	2026-08-21 02:18:55.789017	2026-08-26 23:27:58.28463
\.


--
-- Data for Name: sections; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sections (id, grade_id, section_name, capacity, created_at, updated_at) FROM stdin;
1	1	أ	30	2026-08-21 02:18:55.683456	\N
2	1	ب	30	2026-08-21 02:18:55.683456	\N
3	1	ج	30	2026-08-21 02:18:55.683456	\N
4	2	أ	30	2026-08-21 02:18:55.683456	\N
5	2	ب	30	2026-08-21 02:18:55.683456	\N
6	2	ج	30	2026-08-21 02:18:55.683456	\N
7	3	أ	30	2026-08-21 02:18:55.683456	\N
8	3	ب	30	2026-08-21 02:18:55.683456	\N
9	3	ج	30	2026-08-21 02:18:55.683456	\N
10	4	أ	30	2026-08-21 02:18:55.683456	\N
11	4	ب	30	2026-08-21 02:18:55.683456	\N
12	4	ج	30	2026-08-21 02:18:55.683456	\N
13	5	أ	30	2026-08-21 02:18:55.683456	\N
14	5	ب	30	2026-08-21 02:18:55.683456	\N
15	5	ج	30	2026-08-21 02:18:55.683456	\N
16	6	أ	30	2026-08-21 02:18:55.683456	\N
17	6	ب	30	2026-08-21 02:18:55.683456	\N
18	6	ج	30	2026-08-21 02:18:55.683456	\N
19	7	أ	35	2026-08-21 02:18:55.683456	\N
20	7	ب	35	2026-08-21 02:18:55.683456	\N
21	7	ج	35	2026-08-21 02:18:55.683456	\N
22	8	أ	35	2026-08-21 02:18:55.683456	\N
23	8	ب	35	2026-08-21 02:18:55.683456	\N
24	8	ج	35	2026-08-21 02:18:55.683456	\N
25	9	أ	35	2026-08-21 02:18:55.683456	\N
26	9	ب	35	2026-08-21 02:18:55.683456	\N
27	9	ج	35	2026-08-21 02:18:55.683456	\N
31	11	أ	40	2026-08-21 02:18:55.683456	\N
32	11	ب	40	2026-08-21 02:18:55.683456	\N
33	11	ج	40	2026-08-21 02:18:55.683456	\N
57	10	أ	40	2026-08-30 13:28:35.363585	\N
58	10	ب	40	2026-08-30 13:28:35.363585	\N
59	10	ج	40	2026-08-30 13:28:35.363585	\N
68	12	أ	40	2026-08-30 14:58:56.959893	\N
69	12	ب	40	2026-08-30 14:58:56.959893	\N
70	12	ج	40	2026-08-30 14:58:56.959893	\N
71	12	د	40	2026-08-30 14:58:56.959893	\N
\.


--
-- Data for Name: student_academic_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.student_academic_history (id, student_id, academic_year_id, grade_id, section_id, final_result, promotion_status, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: student_documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.student_documents (id, student_id, document_type, file_path, uploaded_at, created_at, updated_at) FROM stdin;
1	3	شهادة ميلاد	uploads\\documents\\ST-01-0003_20260829_043941_س.jpg	2026-08-29 04:39:41.944645	2026-08-29 04:39:41.944645	\N
\.


--
-- Data for Name: student_fees; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.student_fees (id, student_id, academic_year_id, previous_debt, current_year_fees, discount_amount, net_total_required, created_at, updated_at) FROM stdin;
1	1	1	0.00	0.00	1177.00	-1177.00	2026-08-24 22:59:44.680752	\N
2	2	1	0.00	374099.00	11044.00	363055.00	2026-08-24 22:59:44.680752	\N
5	5	1	0.00	374099.00	19624.00	354475.00	2026-08-24 22:59:44.680752	\N
6	6	1	0.00	374099.00	15556.00	358543.00	2026-08-24 22:59:44.680752	\N
7	7	1	0.00	374099.00	11290.00	362809.00	2026-08-24 22:59:44.680752	\N
8	8	1	0.00	374099.00	4131.00	369968.00	2026-08-24 22:59:44.680752	\N
9	9	1	0.00	374099.00	17315.00	356784.00	2026-08-24 22:59:44.680752	\N
10	10	1	0.00	374099.00	5309.00	368790.00	2026-08-24 22:59:44.680752	\N
11	11	1	0.00	374099.00	15066.00	359033.00	2026-08-24 22:59:44.680752	\N
12	12	1	0.00	374099.00	11249.00	362850.00	2026-08-24 22:59:44.680752	\N
13	13	1	0.00	374099.00	10734.00	363365.00	2026-08-24 22:59:44.680752	\N
14	14	1	0.00	374099.00	7356.00	366743.00	2026-08-24 22:59:44.680752	\N
15	15	1	7073.00	374099.00	4531.00	376641.00	2026-08-24 22:59:44.680752	\N
16	16	1	0.00	374099.00	18920.00	355179.00	2026-08-24 22:59:44.680752	\N
17	17	1	0.00	374099.00	1906.00	372193.00	2026-08-24 22:59:44.680752	\N
18	18	1	3447.00	374099.00	14924.00	362622.00	2026-08-24 22:59:44.680752	\N
19	19	1	30940.00	374099.00	18292.00	386747.00	2026-08-24 22:59:44.680752	\N
20	20	1	0.00	374099.00	8172.00	365927.00	2026-08-24 22:59:44.680752	\N
21	21	1	0.00	374099.00	14390.00	359709.00	2026-08-24 22:59:44.680752	\N
22	22	1	28411.00	374099.00	15383.00	387127.00	2026-08-24 22:59:44.680752	\N
23	23	1	14465.00	374099.00	11673.00	376891.00	2026-08-24 22:59:44.680752	\N
24	24	1	25686.00	374099.00	18935.00	380850.00	2026-08-24 22:59:44.680752	\N
25	25	1	0.00	374099.00	750.00	373349.00	2026-08-24 22:59:44.680752	\N
26	26	1	0.00	374099.00	13853.00	360246.00	2026-08-24 22:59:44.680752	\N
27	27	1	2679.00	374099.00	17680.00	359098.00	2026-08-24 22:59:44.680752	\N
28	28	1	0.00	374099.00	13700.00	360399.00	2026-08-24 22:59:44.680752	\N
29	29	1	0.00	374099.00	4148.00	369951.00	2026-08-24 22:59:44.680752	\N
30	30	1	0.00	374099.00	13294.00	360805.00	2026-08-24 22:59:44.680752	\N
31	31	1	7195.00	374099.00	14238.00	367056.00	2026-08-24 22:59:44.680752	\N
32	32	1	0.00	374099.00	18912.00	355187.00	2026-08-24 22:59:44.680752	\N
33	33	1	0.00	374099.00	3060.00	371039.00	2026-08-24 22:59:44.680752	\N
34	34	1	44934.00	374099.00	6472.00	412561.00	2026-08-24 22:59:44.680752	\N
35	35	1	0.00	374099.00	4730.00	369369.00	2026-08-24 22:59:44.680752	\N
36	36	1	0.00	374099.00	2686.00	371413.00	2026-08-24 22:59:44.680752	\N
37	37	1	0.00	374099.00	18851.00	355248.00	2026-08-24 22:59:44.680752	\N
38	38	1	12308.00	374099.00	10623.00	375784.00	2026-08-24 22:59:44.680752	\N
39	39	1	0.00	374099.00	11665.00	362434.00	2026-08-24 22:59:44.680752	\N
40	40	1	0.00	374099.00	11107.00	362992.00	2026-08-24 22:59:44.680752	\N
41	41	1	0.00	374099.00	2039.00	372060.00	2026-08-24 22:59:44.680752	\N
42	42	1	43242.00	374099.00	1528.00	415813.00	2026-08-24 22:59:44.680752	\N
43	43	1	23348.00	374099.00	1783.00	395664.00	2026-08-24 22:59:44.680752	\N
44	44	1	0.00	374099.00	10524.00	363575.00	2026-08-24 22:59:44.680752	\N
45	45	1	0.00	374099.00	15687.00	358412.00	2026-08-24 22:59:44.680752	\N
46	46	1	0.00	374099.00	16436.00	357663.00	2026-08-24 22:59:44.680752	\N
47	47	1	0.00	374099.00	5622.00	368477.00	2026-08-24 22:59:44.680752	\N
48	48	1	0.00	374099.00	10261.00	363838.00	2026-08-24 22:59:44.680752	\N
49	49	1	8539.00	374099.00	11038.00	371600.00	2026-08-24 22:59:44.680752	\N
50	50	1	3071.00	374099.00	11286.00	365884.00	2026-08-24 22:59:44.680752	\N
51	51	1	35299.00	407216.00	18985.00	423530.00	2026-08-24 22:59:44.680752	\N
52	52	1	26175.00	407216.00	6278.00	427113.00	2026-08-24 22:59:44.680752	\N
53	53	1	0.00	407216.00	647.00	406569.00	2026-08-24 22:59:44.680752	\N
54	54	1	0.00	407216.00	10045.00	397171.00	2026-08-24 22:59:44.680752	\N
55	55	1	0.00	407216.00	218.00	406998.00	2026-08-24 22:59:44.680752	\N
56	56	1	7441.00	407216.00	6520.00	408137.00	2026-08-24 22:59:44.680752	\N
57	57	1	0.00	407216.00	16091.00	391125.00	2026-08-24 22:59:44.680752	\N
58	58	1	0.00	407216.00	3645.00	403571.00	2026-08-24 22:59:44.680752	\N
59	59	1	0.00	407216.00	8562.00	398654.00	2026-08-24 22:59:44.680752	\N
60	60	1	18198.00	407216.00	4893.00	420521.00	2026-08-24 22:59:44.680752	\N
61	61	1	0.00	407216.00	15599.00	391617.00	2026-08-24 22:59:44.680752	\N
62	62	1	0.00	407216.00	18449.00	388767.00	2026-08-24 22:59:44.680752	\N
63	63	1	0.00	407216.00	10216.00	397000.00	2026-08-24 22:59:44.680752	\N
64	64	1	36294.00	407216.00	6730.00	436780.00	2026-08-24 22:59:44.680752	\N
65	65	1	47223.00	407216.00	8719.00	445720.00	2026-08-24 22:59:44.680752	\N
66	66	1	0.00	407216.00	12416.00	394800.00	2026-08-24 22:59:44.680752	\N
67	67	1	3121.00	407216.00	8775.00	401562.00	2026-08-24 22:59:44.680752	\N
68	68	1	48422.00	407216.00	14282.00	441356.00	2026-08-24 22:59:44.680752	\N
69	69	1	44607.00	407216.00	8999.00	442824.00	2026-08-24 22:59:44.680752	\N
70	70	1	0.00	407216.00	16574.00	390642.00	2026-08-24 22:59:44.680752	\N
71	71	1	0.00	407216.00	3633.00	403583.00	2026-08-24 22:59:44.680752	\N
72	72	1	0.00	407216.00	14708.00	392508.00	2026-08-24 22:59:44.680752	\N
73	73	1	0.00	407216.00	4654.00	402562.00	2026-08-24 22:59:44.680752	\N
74	74	1	0.00	407216.00	18486.00	388730.00	2026-08-24 22:59:44.680752	\N
75	75	1	30801.00	407216.00	2193.00	435824.00	2026-08-24 22:59:44.680752	\N
76	76	1	0.00	407216.00	9640.00	397576.00	2026-08-24 22:59:44.680752	\N
77	77	1	34795.00	407216.00	7445.00	434566.00	2026-08-24 22:59:44.680752	\N
78	78	1	0.00	407216.00	13019.00	394197.00	2026-08-24 22:59:44.680752	\N
79	79	1	0.00	407216.00	11427.00	395789.00	2026-08-24 22:59:44.680752	\N
80	80	1	0.00	407216.00	8813.00	398403.00	2026-08-24 22:59:44.680752	\N
4	4	1	0.00	35883.00	5723.00	30160.00	2026-08-24 22:59:44.680752	2026-09-01 04:35:22.991787
3	3	1	0.00	35883.00	17622.00	18261.00	2026-08-24 22:59:44.680752	2026-09-02 06:07:02.640626
\.


--
-- Data for Name: students; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.students (id, student_number, full_name, mother_name, gender, nationality, status, enrollment_type, student_status_reason, birth_date, birth_village, birth_district, birth_governorate, transferred_from_school, transferred_district, transferred_governorate, transfer_date, academic_year_id, grade_id, section_id, parent_id, photo_url, created_at, updated_at) FROM stdin;
1	ST-01-0001	زينب حسن	قمر	أنثى	يمني	انسحاب	مستجد	\N	2012-06-26	الحارة	الغربية	تعز	\N	\N	\N	\N	1	1	1	73	\N	2026-08-24 22:59:44.680752	\N
2	ST-01-0002	غادة أحمد	بسمة	أنثى	يمني	انسحاب	باقي	\N	2010-03-19	القرية	الجنوبية	إب	\N	\N	\N	\N	1	1	1	4	\N	2026-08-24 22:59:44.680752	\N
3	ST-01-0003	طارق زياد	سارة	ذكر	يمني	مستمر	محول	\N	2010-02-25	المنطقة	الشمالية	تعز	\N	\N	\N	\N	1	1	1	71	\N	2026-08-24 22:59:44.680752	\N
4	ST-01-0004	لؤي سامر	سارة	ذكر	يمني	مستمر	باقي	\N	2017-01-12	الحارة	المدينة	ذمار	\N	\N	\N	\N	1	1	1	51	\N	2026-08-24 22:59:44.680752	\N
5	ST-01-0005	مازن هاني	غادة	ذكر	يمني	مستمر	باقي	\N	2016-08-12	الحارة	المدينة	إب	\N	\N	\N	\N	1	1	1	89	\N	2026-08-24 22:59:44.680752	\N
6	ST-01-0006	تقى سعود	قمر	أنثى	يمني	مستمر	باقي	\N	2017-07-19	القرية	الغربية	ذمار	\N	\N	\N	\N	1	1	1	40	\N	2026-08-24 22:59:44.680752	\N
7	ST-01-0007	تقى سعود	حنان	أنثى	يمني	مستمر	باقي	\N	2014-02-25	الحي	الشرقية	المكلا	\N	\N	\N	\N	1	1	1	96	\N	2026-08-24 22:59:44.680752	\N
8	ST-01-0008	هاشم رائد	أمل	ذكر	يمني	مستمر	باقي	\N	2011-09-12	القرية	الغربية	تعز	\N	\N	\N	\N	1	1	1	92	\N	2026-08-24 22:59:44.680752	\N
9	ST-01-0009	جنات محمد	عائشة	أنثى	يمني	انسحاب	مستجد	\N	2009-02-10	الحارة	المركز	الحديدة	\N	\N	\N	\N	1	1	1	3	\N	2026-08-24 22:59:44.680752	\N
10	ST-01-0010	تميم خالد	فرح	ذكر	يمني	مستمر	محول	\N	2007-01-27	القرية	الشرقية	حضرموت	\N	\N	\N	\N	1	1	1	55	\N	2026-08-24 22:59:44.680752	\N
11	ST-01-0011	لؤي سامر	سلمى	ذكر	يمني	مستمر	باقي	\N	2006-08-14	الحي	الشمالية	ذمار	\N	\N	\N	\N	1	1	1	67	\N	2026-08-24 22:59:44.680752	\N
12	ST-01-0012	جنات محمد	رحمة	أنثى	يمني	مستمر	مستجد	\N	2017-07-01	القرية	الجنوبية	عدن	\N	\N	\N	\N	1	1	1	13	\N	2026-08-24 22:59:44.680752	\N
13	ST-01-0013	طارق زياد	عائشة	ذكر	يمني	مستمر	محول	\N	2012-07-08	القرية	المدينة	الحديدة	\N	\N	\N	\N	1	1	1	45	\N	2026-08-24 22:59:44.680752	\N
14	ST-01-0014	أمل ناصر	خديجة	أنثى	يمني	مستمر	محول	\N	2016-06-14	الحارة	الشمالية	الحديدة	\N	\N	\N	\N	1	1	1	67	\N	2026-08-24 22:59:44.680752	\N
15	ST-01-0015	لينا إبراهيم	نورة	أنثى	يمني	مستمر	محول	\N	2009-07-16	المنطقة	المدينة	الحديدة	\N	\N	\N	\N	1	1	1	6	\N	2026-08-24 22:59:44.680752	\N
16	ST-01-0016	سارة خالد	أمل	أنثى	يمني	مستمر	محول	\N	2010-04-24	الحارة	الغربية	صنعاء	\N	\N	\N	\N	1	1	1	93	\N	2026-08-24 22:59:44.680752	\N
17	ST-01-0017	غادة أحمد	حنان	أنثى	يمني	مستمر	مستجد	\N	2005-12-12	المنطقة	الشمالية	صنعاء	\N	\N	\N	\N	1	1	1	73	\N	2026-08-24 22:59:44.680752	\N
19	ST-01-0019	فارس خالد	قمر	ذكر	يمني	انسحاب	باقي	\N	2016-01-20	الحي	الغربية	تعز	\N	\N	\N	\N	1	1	1	53	\N	2026-08-24 22:59:44.680752	\N
20	ST-01-0020	فهد سعود	نورة	ذكر	يمني	مستمر	باقي	\N	2005-10-01	الحارة	الشرقية	المكلا	\N	\N	\N	\N	1	1	2	53	\N	2026-08-24 22:59:44.680752	\N
21	ST-01-0021	ياسمين إبراهيم	شهد	أنثى	يمني	مستمر	مستجد	\N	2008-04-17	الحارة	الغربية	ذمار	\N	\N	\N	\N	1	1	2	21	\N	2026-08-24 22:59:44.680752	\N
22	ST-01-0022	فرح خالد	جنات	أنثى	يمني	مستمر	محول	\N	2018-07-20	القرية	الجنوبية	تعز	\N	\N	\N	\N	1	1	2	19	\N	2026-08-24 22:59:44.680752	\N
23	ST-01-0023	نضال فؤاد	خديجة	ذكر	يمني	مستمر	باقي	\N	2009-02-02	المنطقة	الشرقية	ذمار	\N	\N	\N	\N	1	1	2	56	\N	2026-08-24 22:59:44.680752	\N
24	ST-01-0024	لينا إبراهيم	شهد	أنثى	يمني	مستمر	مستجد	\N	2009-05-08	الحارة	الغربية	عدن	\N	\N	\N	\N	1	1	2	65	\N	2026-08-24 22:59:44.680752	\N
25	ST-01-0025	ياسمين إبراهيم	فاطمة	أنثى	يمني	مستمر	محول	\N	2012-04-04	الحارة	المركز	تعز	\N	\N	\N	\N	1	1	2	2	\N	2026-08-24 22:59:44.680752	\N
26	ST-01-0026	يحيى عادل	فاطمة	ذكر	يمني	مستمر	محول	\N	2017-12-22	المنطقة	الغربية	عدن	\N	\N	\N	\N	1	1	2	93	\N	2026-08-24 22:59:44.680752	\N
27	ST-01-0027	زينب حسن	رنا	أنثى	يمني	مستمر	باقي	\N	2005-07-19	الشارع	المدينة	حضرموت	\N	\N	\N	\N	1	1	2	25	\N	2026-08-24 22:59:44.680752	\N
28	ST-01-0028	سارة خالد	سلمى	أنثى	يمني	مستمر	محول	\N	2010-07-02	الحارة	الجنوبية	الحديدة	\N	\N	\N	\N	1	1	2	59	\N	2026-08-24 22:59:44.680752	\N
29	ST-01-0029	حنان علي	رنا	أنثى	يمني	مستمر	باقي	\N	2012-10-03	الشارع	الغربية	إب	\N	\N	\N	\N	1	1	2	79	\N	2026-08-24 22:59:44.680752	\N
30	ST-01-0030	مودة عمر	حنان	أنثى	يمني	مستمر	مستجد	\N	2014-12-06	الحي	الشمالية	تعز	\N	\N	\N	\N	1	1	2	37	\N	2026-08-24 22:59:44.680752	\N
31	ST-01-0031	كرم نبيل	عائشة	ذكر	يمني	مستمر	مستجد	\N	2009-09-15	الشارع	الشرقية	الحديدة	\N	\N	\N	\N	1	1	2	98	\N	2026-08-24 22:59:44.680752	\N
32	ST-01-0032	زكريا يحيى	فاطمة	ذكر	يمني	مستمر	باقي	\N	2014-05-24	الحارة	الغربية	تعز	\N	\N	\N	\N	1	1	2	93	\N	2026-08-24 22:59:44.680752	\N
33	ST-01-0033	محمد أحمد	صفاء	ذكر	يمني	مستمر	باقي	\N	2011-03-21	الحارة	الجنوبية	تعز	\N	\N	\N	\N	1	1	2	31	\N	2026-08-24 22:59:44.680752	\N
34	ST-01-0034	عمر خالد	ضحى	ذكر	يمني	مستمر	باقي	\N	2008-11-01	الحارة	المركز	ذمار	\N	\N	\N	\N	1	1	2	72	\N	2026-08-24 22:59:44.680752	\N
35	ST-01-0035	هدى سامي	أمل	أنثى	يمني	مستمر	محول	\N	2005-07-12	الحي	الجنوبية	ذمار	\N	\N	\N	\N	1	1	3	20	\N	2026-08-24 22:59:44.680752	\N
36	ST-01-0036	يحيى عادل	زينب	ذكر	يمني	مستمر	باقي	\N	2018-01-28	الحي	الشمالية	صنعاء	\N	\N	\N	\N	1	1	3	28	\N	2026-08-24 22:59:44.680752	\N
37	ST-01-0037	وسن يوسف	حنان	أنثى	يمني	مستمر	مستجد	\N	2018-05-04	الشارع	الشمالية	حضرموت	\N	\N	\N	\N	1	1	3	94	\N	2026-08-24 22:59:44.680752	\N
38	ST-01-0038	لينا إبراهيم	لينا	أنثى	يمني	مستمر	محول	\N	2011-06-25	الشارع	الشرقية	إب	\N	\N	\N	\N	1	1	3	82	\N	2026-08-24 22:59:44.680752	\N
39	ST-01-0039	فرح خالد	مريم	أنثى	يمني	مستمر	محول	\N	2008-02-20	الحارة	الشمالية	الحديدة	\N	\N	\N	\N	1	1	3	99	\N	2026-08-24 22:59:44.680752	\N
40	ST-01-0040	رنا يوسف	دينا	أنثى	يمني	مستمر	محول	\N	2009-09-23	الشارع	الشرقية	حضرموت	\N	\N	\N	\N	1	1	3	46	\N	2026-08-24 22:59:44.680752	\N
41	ST-01-0041	زكريا يحيى	غادة	ذكر	يمني	مستمر	محول	\N	2013-10-07	القرية	الجنوبية	الحديدة	\N	\N	\N	\N	1	1	3	29	\N	2026-08-24 22:59:44.680752	\N
42	ST-01-0042	نضال فؤاد	مريم	ذكر	يمني	مستمر	محول	\N	2014-06-15	الحارة	المركز	صنعاء	\N	\N	\N	\N	1	1	3	11	\N	2026-08-24 22:59:44.680752	\N
43	ST-01-0043	لمى حسن	شهد	أنثى	يمني	مستمر	مستجد	\N	2013-12-12	الحارة	الشمالية	تعز	\N	\N	\N	\N	1	1	3	79	\N	2026-08-24 22:59:44.680752	\N
44	ST-01-0044	صفاء هشام	نورة	أنثى	يمني	انسحاب	باقي	\N	2017-09-25	الشارع	الجنوبية	عدن	\N	\N	\N	\N	1	1	3	49	\N	2026-08-24 22:59:44.680752	\N
45	ST-01-0045	عمر خالد	ضحى	ذكر	يمني	مستمر	باقي	\N	2009-03-25	المنطقة	الشرقية	تعز	\N	\N	\N	\N	1	1	3	41	\N	2026-08-24 22:59:44.680752	\N
46	ST-01-0046	مودة عمر	هدى	أنثى	يمني	مستمر	باقي	\N	2006-11-06	القرية	الجنوبية	تعز	\N	\N	\N	\N	1	1	3	1	\N	2026-08-24 22:59:44.680752	\N
47	ST-01-0047	حسن يوسف	مريم	ذكر	يمني	مستمر	مستجد	\N	2010-09-25	القرية	المركز	عدن	\N	\N	\N	\N	1	1	3	22	\N	2026-08-24 22:59:44.680752	\N
48	ST-01-0048	ناصر عبدالعزيز	ضحى	ذكر	يمني	مستمر	مستجد	\N	2014-06-11	الحي	الغربية	تعز	\N	\N	\N	\N	1	1	3	63	\N	2026-08-24 22:59:44.680752	\N
49	ST-01-0049	لؤي سامر	غادة	ذكر	يمني	مستمر	باقي	\N	2017-12-28	القرية	الجنوبية	صنعاء	\N	\N	\N	\N	1	1	3	14	\N	2026-08-24 22:59:44.680752	\N
50	ST-01-0050	بسمة فهد	حنان	أنثى	يمني	مستمر	محول	\N	2014-04-05	الشارع	الغربية	تعز	\N	\N	\N	\N	1	1	3	16	\N	2026-08-24 22:59:44.680752	\N
51	ST-01-0051	هاشم رائد	بسمة	ذكر	يمني	مستمر	مستجد	\N	2013-07-01	القرية	الشمالية	حضرموت	\N	\N	\N	\N	1	2	4	82	\N	2026-08-24 22:59:44.680752	\N
52	ST-01-0052	علي حسن	حنان	ذكر	يمني	مستمر	مستجد	\N	2011-11-06	الشارع	الشرقية	إب	\N	\N	\N	\N	1	2	4	13	\N	2026-08-24 22:59:44.680752	\N
53	ST-01-0053	نورة عبدالله	رنا	أنثى	يمني	مستمر	باقي	\N	2007-06-15	المنطقة	المركز	المكلا	\N	\N	\N	\N	1	2	4	79	\N	2026-08-24 22:59:44.680752	\N
54	ST-01-0054	هدى سامي	جنات	أنثى	يمني	مستمر	محول	\N	2009-11-14	الحارة	المدينة	عدن	\N	\N	\N	\N	1	2	4	46	\N	2026-08-24 22:59:44.680752	\N
55	ST-01-0055	ناصر عبدالعزيز	عائشة	ذكر	يمني	مستمر	محول	\N	2014-02-20	الحي	الجنوبية	المكلا	\N	\N	\N	\N	1	2	4	27	\N	2026-08-24 22:59:44.680752	\N
56	ST-01-0056	فرح خالد	تقى	أنثى	يمني	مستمر	باقي	\N	2008-03-15	القرية	الغربية	المكلا	\N	\N	\N	\N	1	2	4	42	\N	2026-08-24 22:59:44.680752	\N
57	ST-01-0057	لؤي سامر	صفاء	ذكر	يمني	مستمر	باقي	\N	2016-01-04	المنطقة	الجنوبية	عدن	\N	\N	\N	\N	1	2	4	59	\N	2026-08-24 22:59:44.680752	\N
58	ST-01-0058	ضحى محمد	بسمة	أنثى	يمني	انسحاب	باقي	\N	2012-08-03	القرية	الجنوبية	حضرموت	\N	\N	\N	\N	1	2	4	76	\N	2026-08-24 22:59:44.680752	\N
59	ST-01-0059	فهد سعود	صفاء	ذكر	يمني	انسحاب	باقي	\N	2007-05-26	الحارة	المدينة	ذمار	\N	\N	\N	\N	1	2	4	86	\N	2026-08-24 22:59:44.680752	\N
60	ST-01-0060	فارس خالد	زينب	ذكر	يمني	مستمر	محول	\N	2014-12-11	الحارة	المدينة	المكلا	\N	\N	\N	\N	1	2	4	95	\N	2026-08-24 22:59:44.680752	\N
61	ST-01-0061	هبة عبدالله	بسمة	أنثى	يمني	مستمر	باقي	\N	2011-04-26	الشارع	المركز	الحديدة	\N	\N	\N	\N	1	2	4	33	\N	2026-08-24 22:59:44.680752	\N
62	ST-01-0062	هدى سامي	صفاء	أنثى	يمني	انسحاب	باقي	\N	2012-01-13	القرية	الجنوبية	حضرموت	\N	\N	\N	\N	1	2	4	47	\N	2026-08-24 22:59:44.680752	\N
63	ST-01-0063	كرم نبيل	دينا	ذكر	يمني	مستمر	محول	\N	2017-04-17	الشارع	الشمالية	ذمار	\N	\N	\N	\N	1	2	4	16	\N	2026-08-24 22:59:44.680752	\N
64	ST-01-0064	نجلاء خالد	دينا	أنثى	يمني	مستمر	مستجد	\N	2018-02-26	الحي	الشمالية	عدن	\N	\N	\N	\N	1	2	4	16	\N	2026-08-24 22:59:44.680752	\N
65	ST-01-0065	فهد سعود	فاطمة	ذكر	يمني	مستمر	محول	\N	2008-11-04	المنطقة	المركز	صنعاء	\N	\N	\N	\N	1	2	4	48	\N	2026-08-24 22:59:44.680752	\N
66	ST-01-0066	بدر حمد	تقى	ذكر	يمني	مستمر	باقي	\N	2012-12-03	الشارع	الشرقية	عدن	\N	\N	\N	\N	1	2	4	32	\N	2026-08-24 22:59:44.680752	\N
67	ST-01-0067	حنان علي	تقى	أنثى	يمني	انسحاب	باقي	\N	2006-11-17	الحي	المدينة	إب	\N	\N	\N	\N	1	2	4	25	\N	2026-08-24 22:59:44.680752	\N
68	ST-01-0068	زينب حسن	صفاء	أنثى	يمني	انسحاب	محول	\N	2012-01-01	القرية	الشمالية	صنعاء	\N	\N	\N	\N	1	2	4	26	\N	2026-08-24 22:59:44.680752	\N
69	ST-01-0069	ضحى محمد	حنان	أنثى	يمني	مستمر	باقي	\N	2017-01-23	الشارع	الجنوبية	حضرموت	\N	\N	\N	\N	1	2	4	11	\N	2026-08-24 22:59:44.680752	\N
70	ST-01-0070	صفاء هشام	هدى	أنثى	يمني	انسحاب	مستجد	\N	2013-01-25	الحارة	الجنوبية	حضرموت	\N	\N	\N	\N	1	2	4	93	\N	2026-08-24 22:59:44.680752	\N
71	ST-01-0071	داود سليمان	عائشة	ذكر	يمني	مستمر	مستجد	\N	2006-11-10	الشارع	الشمالية	حضرموت	\N	\N	\N	\N	1	2	4	23	\N	2026-08-24 22:59:44.680752	\N
72	ST-01-0072	لينا إبراهيم	سارة	أنثى	يمني	مستمر	مستجد	\N	2008-10-26	القرية	الشمالية	إب	\N	\N	\N	\N	1	2	4	63	\N	2026-08-24 22:59:44.680752	\N
73	ST-01-0073	عبدالله عمر	سلمى	ذكر	يمني	مستمر	مستجد	\N	2013-10-11	القرية	المدينة	الحديدة	\N	\N	\N	\N	1	2	5	24	\N	2026-08-24 22:59:44.680752	\N
74	ST-01-0074	بسمة فهد	تقى	أنثى	يمني	مستمر	محول	\N	2014-05-18	الشارع	المركز	حضرموت	\N	\N	\N	\N	1	2	5	77	\N	2026-08-24 22:59:44.680752	\N
75	ST-01-0075	لمى حسن	زينب	أنثى	يمني	مستمر	باقي	\N	2013-12-12	الحي	الشمالية	تعز	\N	\N	\N	\N	1	2	5	94	\N	2026-08-24 22:59:44.680752	\N
77	ST-01-0077	هبة عبدالله	فرح	أنثى	يمني	مستمر	محول	\N	2016-01-08	القرية	الغربية	عدن	\N	\N	\N	\N	1	2	5	96	\N	2026-08-24 22:59:44.680752	\N
78	ST-01-0078	سعيد علي	سارة	ذكر	يمني	مستمر	باقي	\N	2012-06-27	المنطقة	المركز	عدن	\N	\N	\N	\N	1	2	5	92	\N	2026-08-24 22:59:44.680752	\N
79	ST-01-0079	هدى سامي	رحمة	أنثى	يمني	مستمر	مستجد	\N	2011-08-26	الحارة	المركز	ذمار	\N	\N	\N	\N	1	2	5	41	\N	2026-08-24 22:59:44.680752	\N
80	ST-01-0080	فارس خالد	مريم	ذكر	يمني	مستمر	محول	\N	2005-08-14	المنطقة	الغربية	المكلا	\N	\N	\N	\N	1	2	5	1	\N	2026-08-24 22:59:44.680752	\N
81	ST-01-0081	سلطان محمد	شهد	ذكر	يمني	مستمر	محول	\N	2006-12-24	الشارع	المدينة	المكلا	\N	\N	\N	\N	1	2	5	17	\N	2026-08-24 22:59:44.680752	\N
83	ST-01-0083	طلال ناصر	دينا	ذكر	يمني	مستمر	مستجد	\N	2008-06-20	الشارع	الشمالية	المكلا	\N	\N	\N	\N	1	2	5	95	\N	2026-08-24 22:59:44.680752	\N
84	ST-01-0084	سلمى طلال	ضحى	أنثى	يمني	مستمر	مستجد	\N	2006-04-23	المنطقة	المركز	إب	\N	\N	\N	\N	1	2	5	1	\N	2026-08-24 22:59:44.680752	\N
85	ST-01-0085	سارة خالد	سارة	أنثى	يمني	انسحاب	مستجد	\N	2018-06-28	الحي	الجنوبية	المكلا	\N	\N	\N	\N	1	2	5	34	\N	2026-08-24 22:59:44.680752	\N
86	ST-01-0086	محمد أحمد	بسمة	ذكر	يمني	مستمر	باقي	\N	2010-03-23	المنطقة	الشرقية	صنعاء	\N	\N	\N	\N	1	2	5	49	\N	2026-08-24 22:59:44.680752	\N
87	ST-01-0087	نضال فؤاد	حنان	ذكر	يمني	مستمر	باقي	\N	2010-08-25	المنطقة	الشمالية	صنعاء	\N	\N	\N	\N	1	2	5	87	\N	2026-08-24 22:59:44.680752	\N
88	ST-01-0088	أكرم وجيه	ضحى	ذكر	يمني	انسحاب	باقي	\N	2007-03-13	القرية	الجنوبية	حضرموت	\N	\N	\N	\N	1	2	5	62	\N	2026-08-24 22:59:44.680752	\N
89	ST-01-0089	عائشة محمد	غادة	أنثى	يمني	مستمر	باقي	\N	2015-06-16	القرية	الشرقية	عدن	\N	\N	\N	\N	1	2	5	82	\N	2026-08-24 22:59:44.680752	\N
90	ST-01-0090	يوسف إبراهيم	نورة	ذكر	يمني	مستمر	باقي	\N	2014-10-22	الحارة	الشرقية	عدن	\N	\N	\N	\N	1	2	6	28	\N	2026-08-24 22:59:44.680752	\N
91	ST-01-0091	هبة عبدالله	غادة	أنثى	يمني	مستمر	محول	\N	2006-07-23	الحارة	الشرقية	صنعاء	\N	\N	\N	\N	1	2	6	43	\N	2026-08-24 22:59:44.680752	\N
92	ST-01-0092	قيس مالك	نورة	ذكر	يمني	مستمر	باقي	\N	2007-08-26	الشارع	المدينة	المكلا	\N	\N	\N	\N	1	2	6	16	\N	2026-08-24 22:59:44.680752	\N
93	ST-01-0093	ياسمين إبراهيم	شهد	أنثى	يمني	مستمر	محول	\N	2006-12-02	الحارة	المركز	المكلا	\N	\N	\N	\N	1	2	6	42	\N	2026-08-24 22:59:44.680752	\N
94	ST-01-0094	مودة عمر	حنان	أنثى	يمني	مستمر	باقي	\N	2009-01-18	الشارع	المدينة	ذمار	\N	\N	\N	\N	1	2	6	82	\N	2026-08-24 22:59:44.680752	\N
95	ST-01-0095	بلال أحمد	أمل	ذكر	يمني	مستمر	باقي	\N	2012-09-24	الشارع	الغربية	صنعاء	\N	\N	\N	\N	1	2	6	96	\N	2026-08-24 22:59:44.680752	\N
96	ST-01-0096	حسن يوسف	عائشة	ذكر	يمني	مستمر	مستجد	\N	2014-07-02	القرية	المدينة	المكلا	\N	\N	\N	\N	1	2	6	29	\N	2026-08-24 22:59:44.680752	\N
97	ST-01-0097	فارس خالد	لينا	ذكر	يمني	مستمر	مستجد	\N	2006-09-12	القرية	المدينة	تعز	\N	\N	\N	\N	1	2	6	88	\N	2026-08-24 22:59:44.680752	\N
98	ST-01-0098	صفاء هشام	سلمى	أنثى	يمني	مستمر	باقي	\N	2007-10-02	الحي	الغربية	حضرموت	\N	\N	\N	\N	1	2	6	5	\N	2026-08-24 22:59:44.680752	\N
99	ST-01-0099	ناصر عبدالعزيز	قمر	ذكر	يمني	مستمر	مستجد	\N	2017-01-01	القرية	المركز	المكلا	\N	\N	\N	\N	1	2	6	87	\N	2026-08-24 22:59:44.680752	\N
100	ST-01-0100	وسن يوسف	شهد	أنثى	يمني	مستمر	باقي	\N	2007-01-09	القرية	الشرقية	إب	\N	\N	\N	\N	1	2	6	44	\N	2026-08-24 22:59:44.680752	\N
101	ST-01-0101	فاطمة علي	قمر	أنثى	يمني	مستمر	مستجد	\N	2014-05-22	الحي	المركز	الحديدة	\N	\N	\N	\N	1	2	6	36	\N	2026-08-24 22:59:44.680752	\N
102	ST-01-0102	رنا يوسف	نورة	أنثى	يمني	انسحاب	باقي	\N	2016-10-11	الحارة	الغربية	المكلا	\N	\N	\N	\N	1	2	6	17	\N	2026-08-24 22:59:44.680752	\N
103	ST-01-0103	ضحى محمد	لينا	أنثى	يمني	مستمر	باقي	\N	2006-05-16	المنطقة	الشرقية	حضرموت	\N	\N	\N	\N	1	2	6	43	\N	2026-08-24 22:59:44.680752	\N
105	ST-01-0105	محمود سامي	أمل	ذكر	يمني	مستمر	باقي	\N	2016-09-23	الشارع	الغربية	عدن	\N	\N	\N	\N	1	2	6	86	\N	2026-08-24 22:59:44.680752	\N
106	ST-01-0106	سعيد علي	سلمى	ذكر	يمني	مستمر	باقي	\N	2007-04-20	الحي	الشمالية	تعز	\N	\N	\N	\N	1	2	6	19	\N	2026-08-24 22:59:44.680752	\N
107	ST-01-0107	شهد زياد	هدى	أنثى	يمني	مستمر	باقي	\N	2011-01-11	الحارة	الغربية	صنعاء	\N	\N	\N	\N	1	3	7	85	\N	2026-08-24 22:59:44.680752	\N
108	ST-01-0108	لينا إبراهيم	سارة	أنثى	يمني	مستمر	محول	\N	2018-06-19	الشارع	المدينة	حضرموت	\N	\N	\N	\N	1	3	7	71	\N	2026-08-24 22:59:44.680752	\N
109	ST-01-0109	نجلاء خالد	سلمى	أنثى	يمني	مستمر	محول	\N	2011-05-09	المنطقة	الشمالية	صنعاء	\N	\N	\N	\N	1	3	7	27	\N	2026-08-24 22:59:44.680752	\N
110	ST-01-0110	رحمة فهد	لينا	أنثى	يمني	انسحاب	محول	\N	2012-03-27	المنطقة	الجنوبية	ذمار	\N	\N	\N	\N	1	3	7	12	\N	2026-08-24 22:59:44.680752	\N
111	ST-01-0111	أكرم وجيه	خديجة	ذكر	يمني	مستمر	باقي	\N	2016-10-23	الحي	الغربية	إب	\N	\N	\N	\N	1	3	7	11	\N	2026-08-24 22:59:44.680752	\N
112	ST-01-0112	سلمى طلال	قمر	أنثى	يمني	مستمر	باقي	\N	2008-12-25	الحي	المدينة	صنعاء	\N	\N	\N	\N	1	3	7	45	\N	2026-08-24 22:59:44.680752	\N
113	ST-01-0113	شهد زياد	صفاء	أنثى	يمني	انسحاب	محول	\N	2009-04-08	القرية	الشمالية	تعز	\N	\N	\N	\N	1	3	7	100	\N	2026-08-24 22:59:44.680752	\N
114	ST-01-0114	دينا حمد	ضحى	أنثى	يمني	مستمر	محول	\N	2016-02-08	القرية	المدينة	حضرموت	\N	\N	\N	\N	1	3	7	27	\N	2026-08-24 22:59:44.680752	\N
115	ST-01-0115	لؤي سامر	عائشة	ذكر	يمني	مستمر	باقي	\N	2012-10-24	الحي	الشرقية	تعز	\N	\N	\N	\N	1	3	7	75	\N	2026-08-24 22:59:44.680752	\N
116	ST-01-0116	راشد علي	سارة	ذكر	يمني	مستمر	باقي	\N	2005-02-23	الحارة	الغربية	تعز	\N	\N	\N	\N	1	3	7	67	\N	2026-08-24 22:59:44.680752	\N
117	ST-01-0117	نجلاء خالد	نورة	أنثى	يمني	انسحاب	مستجد	\N	2009-03-14	الحي	الجنوبية	إب	\N	\N	\N	\N	1	3	7	91	\N	2026-08-24 22:59:44.680752	\N
118	ST-01-0118	ضحى محمد	حنان	أنثى	يمني	مستمر	باقي	\N	2017-02-21	القرية	الشمالية	المكلا	\N	\N	\N	\N	1	3	7	28	\N	2026-08-24 22:59:44.680752	\N
119	ST-01-0119	طارق زياد	شهد	ذكر	يمني	مستمر	باقي	\N	2016-05-17	الحي	الشمالية	ذمار	\N	\N	\N	\N	1	3	7	62	\N	2026-08-24 22:59:44.680752	\N
120	ST-01-0120	تميم خالد	دينا	ذكر	يمني	مستمر	باقي	\N	2014-02-06	القرية	الشرقية	إب	\N	\N	\N	\N	1	3	7	9	\N	2026-08-24 22:59:44.680752	\N
121	ST-01-0121	بسمة فهد	زينب	أنثى	يمني	انسحاب	باقي	\N	2013-07-09	القرية	المدينة	إب	\N	\N	\N	\N	1	3	7	65	\N	2026-08-24 22:59:44.680752	\N
123	ST-01-0123	رنا يوسف	ضحى	أنثى	يمني	مستمر	محول	\N	2017-03-16	القرية	الشرقية	حضرموت	\N	\N	\N	\N	1	3	7	63	\N	2026-08-24 22:59:44.680752	\N
124	ST-01-0124	بسمة فهد	جنات	أنثى	يمني	مستمر	باقي	\N	2008-01-17	الشارع	الجنوبية	الحديدة	\N	\N	\N	\N	1	3	7	30	\N	2026-08-24 22:59:44.680752	\N
125	ST-01-0125	عائشة محمد	مريم	أنثى	يمني	مستمر	باقي	\N	2007-04-11	الحي	الشرقية	حضرموت	\N	\N	\N	\N	1	3	7	65	\N	2026-08-24 22:59:44.680752	\N
126	ST-01-0126	كرم نبيل	هدى	ذكر	يمني	انسحاب	محول	\N	2006-10-02	الحي	الغربية	حضرموت	\N	\N	\N	\N	1	3	7	46	\N	2026-08-24 22:59:44.680752	\N
127	ST-01-0127	أمل ناصر	لينا	أنثى	يمني	مستمر	باقي	\N	2012-07-17	الحي	المدينة	تعز	\N	\N	\N	\N	1	3	7	91	\N	2026-08-24 22:59:44.680752	\N
128	ST-01-0128	سلطان محمد	لينا	ذكر	يمني	مستمر	باقي	\N	2006-04-26	القرية	الشمالية	حضرموت	\N	\N	\N	\N	1	3	7	73	\N	2026-08-24 22:59:44.680752	\N
129	ST-01-0129	جنات محمد	ضحى	أنثى	يمني	انسحاب	باقي	\N	2012-01-23	الحارة	المدينة	الحديدة	\N	\N	\N	\N	1	3	7	59	\N	2026-08-24 22:59:44.680752	\N
104	ST-01-0104	أمل ناصر	تقى	أنثى	يمني	مستمر	محول	\N	2010-04-11	الشارع	الغربية	صنعاء	\N	\N	\N	\N	1	2	3	99	\N	2026-08-24 22:59:44.680752	2026-08-25 03:39:46.169292
130	ST-01-0130	وائل سامي	نورة	ذكر	يمني	انسحاب	محول	\N	2013-07-25	الحي	الجنوبية	صنعاء	\N	\N	\N	\N	1	3	7	43	\N	2026-08-24 22:59:44.680752	\N
131	ST-01-0131	دينا حمد	تقى	أنثى	يمني	انسحاب	باقي	\N	2009-02-10	المنطقة	الغربية	إب	\N	\N	\N	\N	1	3	8	83	\N	2026-08-24 22:59:44.680752	\N
132	ST-01-0132	نورة عبدالله	عائشة	أنثى	يمني	انسحاب	باقي	\N	2014-05-03	القرية	الجنوبية	تعز	\N	\N	\N	\N	1	3	8	6	\N	2026-08-24 22:59:44.680752	\N
133	ST-01-0133	خالد عبدالله	صفاء	ذكر	يمني	انسحاب	باقي	\N	2005-06-22	الحي	الغربية	عدن	\N	\N	\N	\N	1	3	8	96	\N	2026-08-24 22:59:44.680752	\N
135	ST-01-0135	فاطمة علي	دينا	أنثى	يمني	انسحاب	باقي	\N	2016-06-01	الشارع	المدينة	الحديدة	\N	\N	\N	\N	1	3	8	91	\N	2026-08-24 22:59:44.680752	\N
136	ST-01-0136	فهد سعود	جنات	ذكر	يمني	مستمر	مستجد	\N	2011-03-23	الشارع	المركز	المكلا	\N	\N	\N	\N	1	3	8	28	\N	2026-08-24 22:59:44.680752	\N
137	ST-01-0137	سارة خالد	زينب	أنثى	يمني	مستمر	محول	\N	2009-08-10	القرية	المركز	حضرموت	\N	\N	\N	\N	1	3	8	50	\N	2026-08-24 22:59:44.680752	\N
138	ST-01-0138	لينا إبراهيم	رحمة	أنثى	يمني	مستمر	مستجد	\N	2008-03-16	القرية	المدينة	ذمار	\N	\N	\N	\N	1	3	8	89	\N	2026-08-24 22:59:44.680752	\N
139	ST-01-0139	قمر علي	هدى	أنثى	يمني	انسحاب	محول	\N	2011-02-24	الحارة	المدينة	الحديدة	\N	\N	\N	\N	1	3	8	96	\N	2026-08-24 22:59:44.680752	\N
140	ST-01-0140	هدى سامي	هدى	أنثى	يمني	مستمر	باقي	\N	2007-08-05	المنطقة	المركز	المكلا	\N	\N	\N	\N	1	3	8	75	\N	2026-08-24 22:59:44.680752	\N
141	ST-01-0141	زينب حسن	غادة	أنثى	يمني	مستمر	باقي	\N	2007-07-16	المنطقة	الغربية	إب	\N	\N	\N	\N	1	3	8	85	\N	2026-08-24 22:59:44.680752	\N
142	ST-01-0142	حمزة علي	حنان	ذكر	يمني	انسحاب	باقي	\N	2017-06-15	الحي	المدينة	عدن	\N	\N	\N	\N	1	3	8	35	\N	2026-08-24 22:59:44.680752	\N
143	ST-01-0143	ياسمين إبراهيم	غادة	أنثى	يمني	مستمر	باقي	\N	2014-09-05	الحي	الغربية	حضرموت	\N	\N	\N	\N	1	3	8	66	\N	2026-08-24 22:59:44.680752	\N
144	ST-01-0144	سلطان محمد	نورة	ذكر	يمني	مستمر	باقي	\N	2007-08-18	الحي	الشمالية	المكلا	\N	\N	\N	\N	1	3	8	53	\N	2026-08-24 22:59:44.680752	\N
145	ST-01-0145	زياد هشام	ضحى	ذكر	يمني	انسحاب	باقي	\N	2012-04-15	الحارة	المدينة	تعز	\N	\N	\N	\N	1	3	8	80	\N	2026-08-24 22:59:44.680752	\N
146	ST-01-0146	بدر حمد	سارة	ذكر	يمني	مستمر	مستجد	\N	2008-07-20	القرية	المركز	تعز	\N	\N	\N	\N	1	3	8	94	\N	2026-08-24 22:59:44.680752	\N
147	ST-01-0147	لينا إبراهيم	غادة	أنثى	يمني	مستمر	باقي	\N	2011-05-02	الشارع	الجنوبية	صنعاء	\N	\N	\N	\N	1	3	8	22	\N	2026-08-24 22:59:44.680752	\N
148	ST-01-0148	نجلاء خالد	مريم	أنثى	يمني	مستمر	باقي	\N	2014-04-13	الحارة	الشرقية	صنعاء	\N	\N	\N	\N	1	3	8	95	\N	2026-08-24 22:59:44.680752	\N
149	ST-01-0149	لينا إبراهيم	سارة	أنثى	يمني	مستمر	باقي	\N	2008-06-05	المنطقة	الغربية	عدن	\N	\N	\N	\N	1	3	9	24	\N	2026-08-24 22:59:44.680752	\N
150	ST-01-0150	علي حسن	مريم	ذكر	يمني	انسحاب	باقي	\N	2007-04-15	الحي	الشرقية	الحديدة	\N	\N	\N	\N	1	3	9	31	\N	2026-08-24 22:59:44.680752	\N
151	ST-01-0151	يحيى عادل	هدى	ذكر	يمني	مستمر	مستجد	\N	2013-06-16	الحي	الجنوبية	إب	\N	\N	\N	\N	1	3	9	65	\N	2026-08-24 22:59:44.680752	\N
152	ST-01-0152	سلمى طلال	رنا	أنثى	يمني	مستمر	باقي	\N	2009-04-03	المنطقة	الشرقية	صنعاء	\N	\N	\N	\N	1	3	9	52	\N	2026-08-24 22:59:44.680752	\N
153	ST-01-0153	قيس مالك	صفاء	ذكر	يمني	مستمر	باقي	\N	2017-11-12	الحارة	الشمالية	المكلا	\N	\N	\N	\N	1	3	9	41	\N	2026-08-24 22:59:44.680752	\N
154	ST-01-0154	بسمة فهد	شهد	أنثى	يمني	مستمر	محول	\N	2015-09-18	الحارة	الشرقية	الحديدة	\N	\N	\N	\N	1	3	9	29	\N	2026-08-24 22:59:44.680752	\N
155	ST-01-0155	مازن هاني	دينا	ذكر	يمني	مستمر	محول	\N	2009-06-07	الحارة	المدينة	عدن	\N	\N	\N	\N	1	3	9	86	\N	2026-08-24 22:59:44.680752	\N
156	ST-01-0156	داود سليمان	لينا	ذكر	يمني	مستمر	مستجد	\N	2006-12-09	القرية	المركز	تعز	\N	\N	\N	\N	1	3	9	97	\N	2026-08-24 22:59:44.680752	\N
157	ST-01-0157	يحيى عادل	نورة	ذكر	يمني	مستمر	محول	\N	2014-03-04	الحي	الجنوبية	صنعاء	\N	\N	\N	\N	1	3	9	63	\N	2026-08-24 22:59:44.680752	\N
158	ST-01-0158	وليد طلال	لينا	ذكر	يمني	مستمر	محول	\N	2007-04-23	القرية	المركز	صنعاء	\N	\N	\N	\N	1	3	9	39	\N	2026-08-24 22:59:44.680752	\N
159	ST-01-0159	عائشة محمد	أمل	أنثى	يمني	مستمر	مستجد	\N	2006-08-19	المنطقة	الجنوبية	الحديدة	\N	\N	\N	\N	1	3	9	82	\N	2026-08-24 22:59:44.680752	\N
160	ST-01-0160	زكريا يحيى	ضحى	ذكر	يمني	مستمر	باقي	\N	2012-04-15	المنطقة	الشرقية	إب	\N	\N	\N	\N	1	3	9	41	\N	2026-08-24 22:59:44.680752	\N
161	ST-01-0161	سارة خالد	حنان	أنثى	يمني	مستمر	باقي	\N	2008-03-18	المنطقة	الشرقية	المكلا	\N	\N	\N	\N	1	3	9	78	\N	2026-08-24 22:59:44.680752	\N
162	ST-01-0162	لينا إبراهيم	فاطمة	أنثى	يمني	مستمر	محول	\N	2014-05-25	الحي	الشرقية	إب	\N	\N	\N	\N	1	3	9	34	\N	2026-08-24 22:59:44.680752	\N
163	ST-01-0163	هبة عبدالله	دينا	أنثى	يمني	مستمر	مستجد	\N	2017-01-16	القرية	الشرقية	المكلا	\N	\N	\N	\N	1	3	9	58	\N	2026-08-24 22:59:44.680752	\N
164	ST-01-0164	سارة خالد	سارة	أنثى	يمني	انسحاب	باقي	\N	2010-05-19	القرية	الجنوبية	ذمار	\N	\N	\N	\N	1	3	9	79	\N	2026-08-24 22:59:44.680752	\N
165	ST-01-0165	قمر علي	شهد	أنثى	يمني	مستمر	باقي	\N	2018-12-06	الحي	الشمالية	تعز	\N	\N	\N	\N	1	3	9	49	\N	2026-08-24 22:59:44.680752	\N
166	ST-01-0166	رحمة فهد	صفاء	أنثى	يمني	مستمر	محول	\N	2005-07-12	الحارة	المركز	حضرموت	\N	\N	\N	\N	1	4	10	68	\N	2026-08-24 22:59:44.680752	\N
167	ST-01-0167	زكريا يحيى	سلمى	ذكر	يمني	انسحاب	باقي	\N	2013-07-01	الشارع	الجنوبية	ذمار	\N	\N	\N	\N	1	4	10	30	\N	2026-08-24 22:59:44.680752	\N
168	ST-01-0168	لمى حسن	عائشة	أنثى	يمني	مستمر	محول	\N	2014-09-03	الحي	المركز	الحديدة	\N	\N	\N	\N	1	4	10	14	\N	2026-08-24 22:59:44.680752	\N
169	ST-01-0169	هاشم رائد	رحمة	ذكر	يمني	مستمر	باقي	\N	2007-12-20	المنطقة	الجنوبية	عدن	\N	\N	\N	\N	1	4	10	48	\N	2026-08-24 22:59:44.680752	\N
170	ST-01-0170	طلال ناصر	فرح	ذكر	يمني	انسحاب	باقي	\N	2017-01-16	القرية	الشمالية	ذمار	\N	\N	\N	\N	1	4	10	79	\N	2026-08-24 22:59:44.680752	\N
171	ST-01-0171	سلمى طلال	رنا	أنثى	يمني	انسحاب	باقي	\N	2014-11-09	القرية	المدينة	ذمار	\N	\N	\N	\N	1	4	10	26	\N	2026-08-24 22:59:44.680752	\N
172	ST-01-0172	كرم نبيل	زينب	ذكر	يمني	انسحاب	مستجد	\N	2007-09-03	الحي	المركز	تعز	\N	\N	\N	\N	1	4	10	51	\N	2026-08-24 22:59:44.680752	\N
173	ST-01-0173	داود سليمان	رحمة	ذكر	يمني	مستمر	باقي	\N	2008-10-13	الحارة	الشمالية	تعز	\N	\N	\N	\N	1	4	10	66	\N	2026-08-24 22:59:44.680752	\N
174	ST-01-0174	أنس محمد	دينا	ذكر	يمني	انسحاب	باقي	\N	2011-02-26	القرية	المدينة	صنعاء	\N	\N	\N	\N	1	4	10	42	\N	2026-08-24 22:59:44.680752	\N
175	ST-01-0175	شهد زياد	فرح	أنثى	يمني	مستمر	محول	\N	2017-12-07	المنطقة	المدينة	الحديدة	\N	\N	\N	\N	1	4	10	43	\N	2026-08-24 22:59:44.680752	\N
176	ST-01-0176	هبة عبدالله	غادة	أنثى	يمني	مستمر	باقي	\N	2017-01-06	الحي	المركز	الحديدة	\N	\N	\N	\N	1	4	10	71	\N	2026-08-24 22:59:44.680752	\N
177	ST-01-0177	تقى سعود	رحمة	أنثى	يمني	مستمر	مستجد	\N	2013-09-24	الحارة	الشرقية	حضرموت	\N	\N	\N	\N	1	4	10	13	\N	2026-08-24 22:59:44.680752	\N
178	ST-01-0178	ضحى محمد	دينا	أنثى	يمني	مستمر	محول	\N	2009-05-18	الحي	الشمالية	عدن	\N	\N	\N	\N	1	4	10	18	\N	2026-08-24 22:59:44.680752	\N
179	ST-01-0179	وسن يوسف	تقى	أنثى	يمني	مستمر	باقي	\N	2015-08-08	الحارة	المدينة	إب	\N	\N	\N	\N	1	4	10	88	\N	2026-08-24 22:59:44.680752	\N
180	ST-01-0180	سارة خالد	جنات	أنثى	يمني	مستمر	باقي	\N	2012-07-15	الحي	الشرقية	حضرموت	\N	\N	\N	\N	1	4	10	94	\N	2026-08-24 22:59:44.680752	\N
181	ST-01-0181	يوسف إبراهيم	رحمة	ذكر	يمني	مستمر	محول	\N	2006-05-02	الحارة	المركز	ذمار	\N	\N	\N	\N	1	4	10	26	\N	2026-08-24 22:59:44.680752	\N
182	ST-01-0182	لينا إبراهيم	صفاء	أنثى	يمني	مستمر	مستجد	\N	2010-02-13	الحارة	المركز	عدن	\N	\N	\N	\N	1	4	10	67	\N	2026-08-24 22:59:44.680752	\N
183	ST-01-0183	نجلاء خالد	فرح	أنثى	يمني	مستمر	محول	\N	2006-08-23	القرية	الغربية	الحديدة	\N	\N	\N	\N	1	4	10	10	\N	2026-08-24 22:59:44.680752	\N
184	ST-01-0184	بلال أحمد	مريم	ذكر	يمني	مستمر	محول	\N	2006-06-03	الحارة	المركز	حضرموت	\N	\N	\N	\N	1	4	10	95	\N	2026-08-24 22:59:44.680752	\N
185	ST-01-0185	محمود سامي	جنات	ذكر	يمني	انسحاب	محول	\N	2014-11-16	الحي	الغربية	المكلا	\N	\N	\N	\N	1	4	10	42	\N	2026-08-24 22:59:44.680752	\N
186	ST-01-0186	جنات محمد	رنا	أنثى	يمني	مستمر	مستجد	\N	2015-11-09	القرية	الشرقية	إب	\N	\N	\N	\N	1	4	10	54	\N	2026-08-24 22:59:44.680752	\N
187	ST-01-0187	وسن يوسف	هدى	أنثى	يمني	مستمر	باقي	\N	2005-10-17	الحي	الشرقية	إب	\N	\N	\N	\N	1	4	10	88	\N	2026-08-24 22:59:44.680752	\N
188	ST-01-0188	مودة عمر	فاطمة	أنثى	يمني	انسحاب	محول	\N	2012-10-20	القرية	الشرقية	ذمار	\N	\N	\N	\N	1	4	10	9	\N	2026-08-24 22:59:44.680752	\N
189	ST-01-0189	تميم خالد	سلمى	ذكر	يمني	مستمر	باقي	\N	2014-11-06	الشارع	المركز	ذمار	\N	\N	\N	\N	1	4	10	70	\N	2026-08-24 22:59:44.680752	\N
190	ST-01-0190	داود سليمان	فرح	ذكر	يمني	مستمر	محول	\N	2005-05-02	الشارع	المركز	حضرموت	\N	\N	\N	\N	1	4	10	33	\N	2026-08-24 22:59:44.680752	\N
191	ST-01-0191	نضال فؤاد	صفاء	ذكر	يمني	مستمر	محول	\N	2012-04-04	القرية	الجنوبية	تعز	\N	\N	\N	\N	1	4	11	7	\N	2026-08-24 22:59:44.680752	\N
192	ST-01-0192	تقى سعود	مريم	أنثى	يمني	مستمر	باقي	\N	2007-06-16	الحارة	المركز	ذمار	\N	\N	\N	\N	1	4	11	14	\N	2026-08-24 22:59:44.680752	\N
193	ST-01-0193	مازن هاني	زينب	ذكر	يمني	مستمر	باقي	\N	2015-10-24	الحي	الشمالية	عدن	\N	\N	\N	\N	1	4	11	39	\N	2026-08-24 22:59:44.680752	\N
194	ST-01-0194	ياسمين إبراهيم	قمر	أنثى	يمني	مستمر	باقي	\N	2010-05-26	المنطقة	المدينة	عدن	\N	\N	\N	\N	1	4	11	95	\N	2026-08-24 22:59:44.680752	\N
195	ST-01-0195	تقى سعود	شهد	أنثى	يمني	مستمر	باقي	\N	2010-12-06	القرية	المركز	الحديدة	\N	\N	\N	\N	1	4	11	69	\N	2026-08-24 22:59:44.680752	\N
197	ST-01-0197	ضحى محمد	زينب	أنثى	يمني	مستمر	محول	\N	2016-06-01	الحارة	الغربية	عدن	\N	\N	\N	\N	1	4	11	47	\N	2026-08-24 22:59:44.680752	\N
198	ST-01-0198	قمر علي	فرح	أنثى	يمني	مستمر	مستجد	\N	2010-03-15	المنطقة	الجنوبية	صنعاء	\N	\N	\N	\N	1	4	11	68	\N	2026-08-24 22:59:44.680752	\N
199	ST-01-0199	تقى سعود	خديجة	أنثى	يمني	مستمر	محول	\N	2013-08-18	الحارة	الشرقية	المكلا	\N	\N	\N	\N	1	4	11	67	\N	2026-08-24 22:59:44.680752	\N
200	ST-01-0200	مودة عمر	زينب	أنثى	يمني	مستمر	مستجد	\N	2011-11-07	القرية	الشمالية	حضرموت	\N	\N	\N	\N	1	4	11	58	\N	2026-08-24 22:59:44.680752	\N
201	ST-01-0201	مازن هاني	حنان	ذكر	يمني	مستمر	محول	\N	2010-05-21	الحارة	الشرقية	الحديدة	\N	\N	\N	\N	1	4	11	76	\N	2026-08-24 22:59:44.680752	\N
202	ST-01-0202	سلطان محمد	جنات	ذكر	يمني	مستمر	محول	\N	2017-03-20	الحارة	الشمالية	الحديدة	\N	\N	\N	\N	1	4	11	63	\N	2026-08-24 22:59:44.680752	\N
203	ST-01-0203	بسمة فهد	دينا	أنثى	يمني	مستمر	مستجد	\N	2009-11-12	الشارع	الشمالية	ذمار	\N	\N	\N	\N	1	4	11	46	\N	2026-08-24 22:59:44.680752	\N
205	ST-01-0205	سلمى طلال	شهد	أنثى	يمني	مستمر	باقي	\N	2008-11-24	القرية	الغربية	حضرموت	\N	\N	\N	\N	1	4	11	9	\N	2026-08-24 22:59:44.680752	\N
206	ST-01-0206	راشد علي	هدى	ذكر	يمني	مستمر	باقي	\N	2012-07-26	الحارة	الغربية	ذمار	\N	\N	\N	\N	1	4	11	37	\N	2026-08-24 22:59:44.680752	\N
207	ST-01-0207	فارس خالد	بسمة	ذكر	يمني	مستمر	محول	\N	2007-04-22	المنطقة	الشمالية	صنعاء	\N	\N	\N	\N	1	4	11	1	\N	2026-08-24 22:59:44.680752	\N
208	ST-01-0208	يحيى عادل	جنات	ذكر	يمني	مستمر	محول	\N	2018-06-20	الحارة	الشرقية	تعز	\N	\N	\N	\N	1	4	11	82	\N	2026-08-24 22:59:44.680752	\N
209	ST-01-0209	حنان علي	تقى	أنثى	يمني	انسحاب	مستجد	\N	2008-04-22	الشارع	المركز	الحديدة	\N	\N	\N	\N	1	4	11	51	\N	2026-08-24 22:59:44.680752	\N
211	ST-01-0211	ناصر عبدالعزيز	نورة	ذكر	يمني	مستمر	محول	\N	2015-04-01	الحي	الشرقية	إب	\N	\N	\N	\N	1	4	11	64	\N	2026-08-24 22:59:44.680752	\N
212	ST-01-0212	لمى حسن	أمل	أنثى	يمني	مستمر	باقي	\N	2008-07-13	الشارع	الجنوبية	صنعاء	\N	\N	\N	\N	1	4	11	62	\N	2026-08-24 22:59:44.680752	\N
213	ST-01-0213	علي حسن	جنات	ذكر	يمني	مستمر	باقي	\N	2017-01-24	المنطقة	الغربية	ذمار	\N	\N	\N	\N	1	4	11	22	\N	2026-08-24 22:59:44.680752	\N
214	ST-01-0214	رنا يوسف	صفاء	أنثى	يمني	مستمر	باقي	\N	2013-07-24	الحي	المدينة	صنعاء	\N	\N	\N	\N	1	4	11	33	\N	2026-08-24 22:59:44.680752	\N
215	ST-01-0215	هاشم رائد	لينا	ذكر	يمني	مستمر	باقي	\N	2018-02-04	الشارع	الغربية	صنعاء	\N	\N	\N	\N	1	4	11	89	\N	2026-08-24 22:59:44.680752	\N
216	ST-01-0216	هاشم رائد	شهد	ذكر	يمني	مستمر	باقي	\N	2016-09-18	القرية	الشمالية	تعز	\N	\N	\N	\N	1	4	12	10	\N	2026-08-24 22:59:44.680752	\N
217	ST-01-0217	فاطمة علي	دينا	أنثى	يمني	مستمر	محول	\N	2013-10-22	المنطقة	الشمالية	المكلا	\N	\N	\N	\N	1	4	12	58	\N	2026-08-24 22:59:44.680752	\N
218	ST-01-0218	هبة عبدالله	ضحى	أنثى	يمني	مستمر	باقي	\N	2018-05-15	المنطقة	الشمالية	ذمار	\N	\N	\N	\N	1	4	12	13	\N	2026-08-24 22:59:44.680752	\N
219	ST-01-0219	محمود سامي	هدى	ذكر	يمني	انسحاب	محول	\N	2007-08-21	الحارة	الجنوبية	المكلا	\N	\N	\N	\N	1	4	12	35	\N	2026-08-24 22:59:44.680752	\N
220	ST-01-0220	تقى سعود	حنان	أنثى	يمني	مستمر	باقي	\N	2009-02-27	الحارة	الشمالية	عدن	\N	\N	\N	\N	1	4	12	80	\N	2026-08-24 22:59:44.680752	\N
221	ST-01-0221	تقى سعود	أمل	أنثى	يمني	مستمر	باقي	\N	2015-09-25	الحارة	الشمالية	عدن	\N	\N	\N	\N	1	4	12	62	\N	2026-08-24 22:59:44.680752	\N
222	ST-01-0222	هدى سامي	بسمة	أنثى	يمني	مستمر	محول	\N	2018-07-10	المنطقة	الجنوبية	تعز	\N	\N	\N	\N	1	4	12	68	\N	2026-08-24 22:59:44.680752	\N
223	ST-01-0223	سارة خالد	مريم	أنثى	يمني	مستمر	باقي	\N	2012-04-09	الشارع	الشمالية	إب	\N	\N	\N	\N	1	4	12	50	\N	2026-08-24 22:59:44.680752	\N
224	ST-01-0224	هاشم رائد	لينا	ذكر	يمني	مستمر	مستجد	\N	2013-11-04	الحي	المدينة	عدن	\N	\N	\N	\N	1	4	12	1	\N	2026-08-24 22:59:44.680752	\N
225	ST-01-0225	خديجة عمر	فرح	أنثى	يمني	مستمر	مستجد	\N	2014-01-28	الشارع	الشمالية	صنعاء	\N	\N	\N	\N	1	4	12	23	\N	2026-08-24 22:59:44.680752	\N
226	ST-01-0226	تميم خالد	شهد	ذكر	يمني	مستمر	باقي	\N	2013-06-28	الحي	الجنوبية	حضرموت	\N	\N	\N	\N	1	4	12	86	\N	2026-08-24 22:59:44.680752	\N
227	ST-01-0227	أكرم وجيه	فاطمة	ذكر	يمني	مستمر	مستجد	\N	2012-11-09	الحارة	المدينة	تعز	\N	\N	\N	\N	1	4	12	11	\N	2026-08-24 22:59:44.680752	\N
228	ST-01-0228	هاشم رائد	فرح	ذكر	يمني	انسحاب	محول	\N	2012-10-05	المنطقة	الشرقية	المكلا	\N	\N	\N	\N	1	4	12	29	\N	2026-08-24 22:59:44.680752	\N
229	ST-01-0229	ضحى محمد	رنا	أنثى	يمني	مستمر	باقي	\N	2016-04-22	الشارع	الشمالية	إب	\N	\N	\N	\N	1	4	12	82	\N	2026-08-24 22:59:44.680752	\N
230	ST-01-0230	يحيى عادل	دينا	ذكر	يمني	مستمر	محول	\N	2013-05-08	الحارة	الجنوبية	ذمار	\N	\N	\N	\N	1	4	12	47	\N	2026-08-24 22:59:44.680752	\N
232	ST-01-0232	جنات محمد	خديجة	أنثى	يمني	انسحاب	محول	\N	2007-04-15	الشارع	الشرقية	المكلا	\N	\N	\N	\N	1	4	12	20	\N	2026-08-24 22:59:44.680752	\N
233	ST-01-0233	وليد طلال	رنا	ذكر	يمني	مستمر	باقي	\N	2015-06-27	الحي	الغربية	صنعاء	\N	\N	\N	\N	1	4	12	83	\N	2026-08-24 22:59:44.680752	\N
234	ST-01-0234	غادة أحمد	تقى	أنثى	يمني	مستمر	محول	\N	2018-01-06	المنطقة	الشرقية	إب	\N	\N	\N	\N	1	4	12	20	\N	2026-08-24 22:59:44.680752	\N
235	ST-01-0235	هدى سامي	صفاء	أنثى	يمني	مستمر	محول	\N	2008-04-08	الحارة	المركز	المكلا	\N	\N	\N	\N	1	4	12	7	\N	2026-08-24 22:59:44.680752	\N
236	ST-01-0236	حمزة علي	شهد	ذكر	يمني	انسحاب	باقي	\N	2018-06-09	القرية	الجنوبية	تعز	\N	\N	\N	\N	1	4	12	95	\N	2026-08-24 22:59:44.680752	\N
237	ST-01-0237	فاطمة علي	حنان	أنثى	يمني	مستمر	باقي	\N	2011-02-18	الشارع	الغربية	عدن	\N	\N	\N	\N	1	4	12	14	\N	2026-08-24 22:59:44.680752	\N
238	ST-01-0238	فهد سعود	خديجة	ذكر	يمني	مستمر	باقي	\N	2013-11-13	الحارة	الشرقية	ذمار	\N	\N	\N	\N	1	4	12	86	\N	2026-08-24 22:59:44.680752	\N
239	ST-01-0239	طلال ناصر	حنان	ذكر	يمني	مستمر	باقي	\N	2005-06-24	الحي	المركز	حضرموت	\N	\N	\N	\N	1	5	13	61	\N	2026-08-24 22:59:44.680752	\N
240	ST-01-0240	حسن يوسف	أمل	ذكر	يمني	انسحاب	محول	\N	2015-09-08	القرية	الجنوبية	عدن	\N	\N	\N	\N	1	5	13	6	\N	2026-08-24 22:59:44.680752	\N
242	ST-01-0242	لمى حسن	فاطمة	أنثى	يمني	مستمر	باقي	\N	2010-04-22	القرية	الغربية	تعز	\N	\N	\N	\N	1	5	13	45	\N	2026-08-24 22:59:44.680752	\N
243	ST-01-0243	نورة عبدالله	هدى	أنثى	يمني	مستمر	مستجد	\N	2015-01-07	الشارع	المركز	المكلا	\N	\N	\N	\N	1	5	13	93	\N	2026-08-24 22:59:44.680752	\N
244	ST-01-0244	نجلاء خالد	صفاء	أنثى	يمني	انسحاب	مستجد	\N	2017-06-17	الحي	المركز	صنعاء	\N	\N	\N	\N	1	5	13	12	\N	2026-08-24 22:59:44.680752	\N
245	ST-01-0245	فرح خالد	رحمة	أنثى	يمني	مستمر	باقي	\N	2014-01-18	الحارة	المركز	إب	\N	\N	\N	\N	1	5	13	6	\N	2026-08-24 22:59:44.680752	\N
246	ST-01-0246	قمر علي	سارة	أنثى	يمني	مستمر	باقي	\N	2007-01-20	القرية	المركز	ذمار	\N	\N	\N	\N	1	5	13	21	\N	2026-08-24 22:59:44.680752	\N
247	ST-01-0247	طارق زياد	فرح	ذكر	يمني	مستمر	محول	\N	2012-12-20	الشارع	المركز	عدن	\N	\N	\N	\N	1	5	13	44	\N	2026-08-24 22:59:44.680752	\N
248	ST-01-0248	رحمة فهد	صفاء	أنثى	يمني	مستمر	باقي	\N	2012-12-25	المنطقة	المركز	حضرموت	\N	\N	\N	\N	1	5	13	70	\N	2026-08-24 22:59:44.680752	\N
249	ST-01-0249	سارة خالد	خديجة	أنثى	يمني	انسحاب	باقي	\N	2007-04-18	الحارة	الجنوبية	إب	\N	\N	\N	\N	1	5	13	6	\N	2026-08-24 22:59:44.680752	\N
250	ST-01-0250	عاصم عمر	بسمة	ذكر	يمني	مستمر	محول	\N	2010-04-18	الحارة	الغربية	صنعاء	\N	\N	\N	\N	1	5	13	72	\N	2026-08-24 22:59:44.680752	\N
251	ST-01-0251	حنان علي	شهد	أنثى	يمني	مستمر	باقي	\N	2010-02-19	القرية	المدينة	ذمار	\N	\N	\N	\N	1	5	13	21	\N	2026-08-24 22:59:44.680752	\N
252	ST-01-0252	حمزة علي	هدى	ذكر	يمني	مستمر	مستجد	\N	2008-07-24	الشارع	الجنوبية	صنعاء	\N	\N	\N	\N	1	5	13	97	\N	2026-08-24 22:59:44.680752	\N
253	ST-01-0253	سعيد علي	سلمى	ذكر	يمني	مستمر	باقي	\N	2016-08-19	الحارة	الشمالية	حضرموت	\N	\N	\N	\N	1	5	13	94	\N	2026-08-24 22:59:44.680752	\N
254	ST-01-0254	فرح خالد	دينا	أنثى	يمني	مستمر	باقي	\N	2018-03-23	القرية	المركز	تعز	\N	\N	\N	\N	1	5	13	55	\N	2026-08-24 22:59:44.680752	\N
255	ST-01-0255	زكريا يحيى	صفاء	ذكر	يمني	مستمر	محول	\N	2014-01-18	الحي	المدينة	عدن	\N	\N	\N	\N	1	5	13	66	\N	2026-08-24 22:59:44.680752	\N
256	ST-01-0256	أكرم وجيه	جنات	ذكر	يمني	انسحاب	مستجد	\N	2016-12-06	القرية	المركز	المكلا	\N	\N	\N	\N	1	5	13	40	\N	2026-08-24 22:59:44.680752	\N
257	ST-01-0257	فهد سعود	تقى	ذكر	يمني	مستمر	باقي	\N	2015-08-27	الحي	الغربية	المكلا	\N	\N	\N	\N	1	5	13	71	\N	2026-08-24 22:59:44.680752	\N
259	ST-01-0259	بدر حمد	تقى	ذكر	يمني	مستمر	محول	\N	2018-04-10	المنطقة	الجنوبية	عدن	\N	\N	\N	\N	1	5	13	30	\N	2026-08-24 22:59:44.680752	\N
260	ST-01-0260	نورة عبدالله	بسمة	أنثى	يمني	مستمر	محول	\N	2016-03-25	القرية	الجنوبية	الحديدة	\N	\N	\N	\N	1	5	14	52	\N	2026-08-24 22:59:44.680752	\N
261	ST-01-0261	رحمة فهد	صفاء	أنثى	يمني	مستمر	مستجد	\N	2016-12-21	الشارع	الشرقية	حضرموت	\N	\N	\N	\N	1	5	14	65	\N	2026-08-24 22:59:44.680752	\N
262	ST-01-0262	سعيد علي	سلمى	ذكر	يمني	انسحاب	محول	\N	2014-06-06	المنطقة	الشرقية	عدن	\N	\N	\N	\N	1	5	14	51	\N	2026-08-24 22:59:44.680752	\N
263	ST-01-0263	بسمة فهد	حنان	أنثى	يمني	مستمر	باقي	\N	2016-12-20	الحارة	الجنوبية	تعز	\N	\N	\N	\N	1	5	14	19	\N	2026-08-24 22:59:44.680752	\N
264	ST-01-0264	آدم نوح	غادة	ذكر	يمني	مستمر	باقي	\N	2013-06-21	الحي	الغربية	صنعاء	\N	\N	\N	\N	1	5	14	93	\N	2026-08-24 22:59:44.680752	\N
265	ST-01-0265	محمد أحمد	تقى	ذكر	يمني	مستمر	باقي	\N	2016-12-13	القرية	الغربية	عدن	\N	\N	\N	\N	1	5	14	78	\N	2026-08-24 22:59:44.680752	\N
266	ST-01-0266	قيس مالك	أمل	ذكر	يمني	مستمر	محول	\N	2005-01-01	الشارع	المدينة	حضرموت	\N	\N	\N	\N	1	5	14	39	\N	2026-08-24 22:59:44.680752	\N
267	ST-01-0267	ماجد فهد	صفاء	ذكر	يمني	مستمر	مستجد	\N	2005-05-06	الحارة	الشرقية	عدن	\N	\N	\N	\N	1	5	14	86	\N	2026-08-24 22:59:44.680752	\N
268	ST-01-0268	نورة عبدالله	نورة	أنثى	يمني	مستمر	مستجد	\N	2016-12-20	الحي	الجنوبية	المكلا	\N	\N	\N	\N	1	5	14	65	\N	2026-08-24 22:59:44.680752	\N
269	ST-01-0269	نجلاء خالد	خديجة	أنثى	يمني	مستمر	مستجد	\N	2013-01-02	الحي	الشرقية	عدن	\N	\N	\N	\N	1	5	14	6	\N	2026-08-24 22:59:44.680752	\N
270	ST-01-0270	تميم خالد	رنا	ذكر	يمني	مستمر	باقي	\N	2009-02-19	المنطقة	الشمالية	إب	\N	\N	\N	\N	1	5	14	88	\N	2026-08-24 22:59:44.680752	\N
271	ST-01-0271	فرح خالد	صفاء	أنثى	يمني	انسحاب	محول	\N	2017-01-12	المنطقة	الغربية	عدن	\N	\N	\N	\N	1	5	14	44	\N	2026-08-24 22:59:44.680752	\N
272	ST-01-0272	بسمة فهد	زينب	أنثى	يمني	مستمر	محول	\N	2017-09-25	الشارع	الشرقية	تعز	\N	\N	\N	\N	1	5	14	24	\N	2026-08-24 22:59:44.680752	\N
273	ST-01-0273	كرم نبيل	أمل	ذكر	يمني	مستمر	مستجد	\N	2012-10-01	الحي	المدينة	تعز	\N	\N	\N	\N	1	5	14	34	\N	2026-08-24 22:59:44.680752	\N
274	ST-01-0274	لمى حسن	نورة	أنثى	يمني	مستمر	باقي	\N	2016-06-19	الحارة	المدينة	المكلا	\N	\N	\N	\N	1	5	14	49	\N	2026-08-24 22:59:44.680752	\N
275	ST-01-0275	زياد هشام	فرح	ذكر	يمني	مستمر	باقي	\N	2009-11-03	القرية	المدينة	الحديدة	\N	\N	\N	\N	1	5	15	7	\N	2026-08-24 22:59:44.680752	\N
276	ST-01-0276	شهد زياد	جنات	أنثى	يمني	مستمر	باقي	\N	2009-12-27	الشارع	الجنوبية	صنعاء	\N	\N	\N	\N	1	5	15	31	\N	2026-08-24 22:59:44.680752	\N
277	ST-01-0277	رحمة فهد	فاطمة	أنثى	يمني	مستمر	مستجد	\N	2014-09-04	الحي	الغربية	إب	\N	\N	\N	\N	1	5	15	73	\N	2026-08-24 22:59:44.680752	\N
278	ST-01-0278	زياد هشام	فرح	ذكر	يمني	انسحاب	محول	\N	2014-04-22	الحي	الشرقية	صنعاء	\N	\N	\N	\N	1	5	15	63	\N	2026-08-24 22:59:44.680752	\N
279	ST-01-0279	قمر علي	قمر	أنثى	يمني	مستمر	مستجد	\N	2010-05-23	الحارة	الشرقية	عدن	\N	\N	\N	\N	1	5	15	17	\N	2026-08-24 22:59:44.680752	\N
280	ST-01-0280	عمر خالد	سارة	ذكر	يمني	مستمر	محول	\N	2011-06-08	الحارة	الجنوبية	المكلا	\N	\N	\N	\N	1	5	15	26	\N	2026-08-24 22:59:44.680752	\N
281	ST-01-0281	غادة أحمد	خديجة	أنثى	يمني	مستمر	محول	\N	2016-05-27	القرية	الشرقية	الحديدة	\N	\N	\N	\N	1	5	15	44	\N	2026-08-24 22:59:44.680752	\N
282	ST-01-0282	كرم نبيل	عائشة	ذكر	يمني	مستمر	محول	\N	2013-11-26	الشارع	الشرقية	ذمار	\N	\N	\N	\N	1	5	15	73	\N	2026-08-24 22:59:44.680752	\N
283	ST-01-0283	هاشم رائد	غادة	ذكر	يمني	مستمر	مستجد	\N	2005-09-14	المنطقة	الغربية	إب	\N	\N	\N	\N	1	5	15	99	\N	2026-08-24 22:59:44.680752	\N
284	ST-01-0284	شهد زياد	جنات	أنثى	يمني	مستمر	باقي	\N	2011-04-01	الحارة	المدينة	ذمار	\N	\N	\N	\N	1	5	15	17	\N	2026-08-24 22:59:44.680752	\N
285	ST-01-0285	أمل ناصر	دينا	أنثى	يمني	انسحاب	محول	\N	2014-11-05	الحارة	الجنوبية	المكلا	\N	\N	\N	\N	1	5	15	6	\N	2026-08-24 22:59:44.680752	\N
286	ST-01-0286	سلمى طلال	سلمى	أنثى	يمني	مستمر	محول	\N	2018-07-05	الحي	الشرقية	المكلا	\N	\N	\N	\N	1	5	15	13	\N	2026-08-24 22:59:44.680752	\N
287	ST-01-0287	سلمى طلال	مريم	أنثى	يمني	مستمر	باقي	\N	2018-04-10	الحي	الغربية	صنعاء	\N	\N	\N	\N	1	5	15	31	\N	2026-08-24 22:59:44.680752	\N
288	ST-01-0288	سلمى طلال	سارة	أنثى	يمني	مستمر	باقي	\N	2017-03-18	الحي	الجنوبية	تعز	\N	\N	\N	\N	1	5	15	3	\N	2026-08-24 22:59:44.680752	\N
289	ST-01-0289	وسن يوسف	أمل	أنثى	يمني	مستمر	مستجد	\N	2005-06-22	الشارع	المدينة	عدن	\N	\N	\N	\N	1	5	15	41	\N	2026-08-24 22:59:44.680752	\N
290	ST-01-0290	لينا إبراهيم	رنا	أنثى	يمني	مستمر	مستجد	\N	2010-06-10	المنطقة	المدينة	ذمار	\N	\N	\N	\N	1	5	15	13	\N	2026-08-24 22:59:44.680752	\N
291	ST-01-0291	فهد سعود	شهد	ذكر	يمني	مستمر	باقي	\N	2005-07-04	الحارة	الشرقية	عدن	\N	\N	\N	\N	1	5	15	28	\N	2026-08-24 22:59:44.680752	\N
292	ST-01-0292	عائشة محمد	قمر	أنثى	يمني	انسحاب	باقي	\N	2016-08-01	المنطقة	المدينة	إب	\N	\N	\N	\N	1	5	15	89	\N	2026-08-24 22:59:44.680752	\N
293	ST-01-0293	نضال فؤاد	بسمة	ذكر	يمني	مستمر	محول	\N	2017-02-10	الشارع	الشمالية	حضرموت	\N	\N	\N	\N	1	5	15	77	\N	2026-08-24 22:59:44.680752	\N
294	ST-01-0294	بدر حمد	خديجة	ذكر	يمني	مستمر	مستجد	\N	2015-04-06	الشارع	الشمالية	تعز	\N	\N	\N	\N	1	6	16	83	\N	2026-08-24 22:59:44.680752	\N
295	ST-01-0295	لؤي سامر	فرح	ذكر	يمني	مستمر	محول	\N	2008-03-23	الشارع	الغربية	تعز	\N	\N	\N	\N	1	6	16	89	\N	2026-08-24 22:59:44.680752	\N
296	ST-01-0296	هاشم رائد	نورة	ذكر	يمني	مستمر	مستجد	\N	2018-08-26	الشارع	الشمالية	ذمار	\N	\N	\N	\N	1	6	16	98	\N	2026-08-24 22:59:44.680752	\N
297	ST-01-0297	محمد أحمد	بسمة	ذكر	يمني	انسحاب	مستجد	\N	2015-06-20	القرية	الشرقية	عدن	\N	\N	\N	\N	1	6	16	96	\N	2026-08-24 22:59:44.680752	\N
298	ST-01-0298	راشد علي	رنا	ذكر	يمني	مستمر	باقي	\N	2013-04-11	القرية	الشرقية	المكلا	\N	\N	\N	\N	1	6	16	76	\N	2026-08-24 22:59:44.680752	\N
299	ST-01-0299	فهد سعود	دينا	ذكر	يمني	مستمر	باقي	\N	2008-11-20	القرية	المدينة	حضرموت	\N	\N	\N	\N	1	6	16	98	\N	2026-08-24 22:59:44.680752	\N
301	ST-01-0301	بلال أحمد	تقى	ذكر	يمني	مستمر	باقي	\N	2013-06-08	الشارع	الجنوبية	إب	\N	\N	\N	\N	1	6	16	40	\N	2026-08-24 22:59:44.680752	\N
302	ST-01-0302	نجلاء خالد	حنان	أنثى	يمني	مستمر	محول	\N	2011-12-23	الحي	الجنوبية	حضرموت	\N	\N	\N	\N	1	6	16	40	\N	2026-08-24 22:59:44.680752	\N
303	ST-01-0303	لمى حسن	خديجة	أنثى	يمني	انسحاب	باقي	\N	2005-12-06	القرية	الغربية	الحديدة	\N	\N	\N	\N	1	6	16	49	\N	2026-08-24 22:59:44.680752	\N
304	ST-01-0304	رحمة فهد	هدى	أنثى	يمني	مستمر	محول	\N	2012-11-10	الحارة	الغربية	الحديدة	\N	\N	\N	\N	1	6	16	50	\N	2026-08-24 22:59:44.680752	\N
305	ST-01-0305	محمد أحمد	ضحى	ذكر	يمني	مستمر	محول	\N	2014-04-13	القرية	الشمالية	صنعاء	\N	\N	\N	\N	1	6	16	82	\N	2026-08-24 22:59:44.680752	\N
306	ST-01-0306	هاشم رائد	دينا	ذكر	يمني	انسحاب	باقي	\N	2005-06-15	الحي	الغربية	تعز	\N	\N	\N	\N	1	6	16	53	\N	2026-08-24 22:59:44.680752	\N
307	ST-01-0307	قمر علي	لينا	أنثى	يمني	انسحاب	باقي	\N	2017-10-18	الحي	الشرقية	المكلا	\N	\N	\N	\N	1	6	16	100	\N	2026-08-24 22:59:44.680752	\N
308	ST-01-0308	طارق زياد	مريم	ذكر	يمني	مستمر	محول	\N	2018-09-02	الشارع	المركز	عدن	\N	\N	\N	\N	1	6	16	65	\N	2026-08-24 22:59:44.680752	\N
309	ST-01-0309	مازن هاني	سلمى	ذكر	يمني	مستمر	باقي	\N	2006-04-18	القرية	الشرقية	المكلا	\N	\N	\N	\N	1	6	16	57	\N	2026-08-24 22:59:44.680752	\N
310	ST-01-0310	مريم أحمد	رحمة	أنثى	يمني	انسحاب	مستجد	\N	2017-04-10	الحي	المركز	تعز	\N	\N	\N	\N	1	6	16	50	\N	2026-08-24 22:59:44.680752	\N
311	ST-01-0311	علي حسن	صفاء	ذكر	يمني	مستمر	باقي	\N	2014-10-26	الحي	المركز	الحديدة	\N	\N	\N	\N	1	6	16	96	\N	2026-08-24 22:59:44.680752	\N
312	ST-01-0312	زكريا يحيى	شهد	ذكر	يمني	مستمر	باقي	\N	2017-10-19	الحي	الجنوبية	صنعاء	\N	\N	\N	\N	1	6	16	56	\N	2026-08-24 22:59:44.680752	\N
313	ST-01-0313	فرح خالد	غادة	أنثى	يمني	مستمر	باقي	\N	2010-08-25	الشارع	المدينة	المكلا	\N	\N	\N	\N	1	6	17	16	\N	2026-08-24 22:59:44.680752	\N
314	ST-01-0314	أمل ناصر	زينب	أنثى	يمني	مستمر	مستجد	\N	2005-05-11	الشارع	الجنوبية	إب	\N	\N	\N	\N	1	6	17	38	\N	2026-08-24 22:59:44.680752	\N
315	ST-01-0315	شهد زياد	رنا	أنثى	يمني	مستمر	محول	\N	2005-06-01	الشارع	الجنوبية	المكلا	\N	\N	\N	\N	1	6	17	26	\N	2026-08-24 22:59:44.680752	\N
316	ST-01-0316	سارة خالد	فرح	أنثى	يمني	مستمر	محول	\N	2008-07-25	الحي	المركز	إب	\N	\N	\N	\N	1	6	17	91	\N	2026-08-24 22:59:44.680752	\N
317	ST-01-0317	سارة خالد	شهد	أنثى	يمني	مستمر	باقي	\N	2018-03-15	الشارع	المركز	تعز	\N	\N	\N	\N	1	6	17	52	\N	2026-08-24 22:59:44.680752	\N
318	ST-01-0318	طلال ناصر	نورة	ذكر	يمني	مستمر	باقي	\N	2018-06-03	المنطقة	الغربية	حضرموت	\N	\N	\N	\N	1	6	17	46	\N	2026-08-24 22:59:44.680752	\N
319	ST-01-0319	عاصم عمر	رحمة	ذكر	يمني	مستمر	باقي	\N	2015-10-05	الشارع	المدينة	المكلا	\N	\N	\N	\N	1	6	17	73	\N	2026-08-24 22:59:44.680752	\N
320	ST-01-0320	ياسمين إبراهيم	ضحى	أنثى	يمني	مستمر	محول	\N	2014-08-14	الحارة	الشرقية	الحديدة	\N	\N	\N	\N	1	6	17	59	\N	2026-08-24 22:59:44.680752	\N
321	ST-01-0321	رحمة فهد	هدى	أنثى	يمني	مستمر	مستجد	\N	2005-11-12	القرية	الشرقية	تعز	\N	\N	\N	\N	1	6	17	9	\N	2026-08-24 22:59:44.680752	\N
322	ST-01-0322	علي حسن	بسمة	ذكر	يمني	مستمر	مستجد	\N	2017-08-08	الحي	الجنوبية	صنعاء	\N	\N	\N	\N	1	6	17	93	\N	2026-08-24 22:59:44.680752	\N
323	ST-01-0323	صفاء هشام	رنا	أنثى	يمني	مستمر	محول	\N	2008-08-07	القرية	الجنوبية	الحديدة	\N	\N	\N	\N	1	6	17	57	\N	2026-08-24 22:59:44.680752	\N
324	ST-01-0324	فرح خالد	زينب	أنثى	يمني	انسحاب	محول	\N	2012-06-06	المنطقة	المدينة	الحديدة	\N	\N	\N	\N	1	6	17	48	\N	2026-08-24 22:59:44.680752	\N
325	ST-01-0325	حسن يوسف	عائشة	ذكر	يمني	مستمر	مستجد	\N	2015-10-27	القرية	المدينة	صنعاء	\N	\N	\N	\N	1	6	17	6	\N	2026-08-24 22:59:44.680752	\N
326	ST-01-0326	سلطان محمد	تقى	ذكر	يمني	مستمر	مستجد	\N	2006-05-25	القرية	الجنوبية	تعز	\N	\N	\N	\N	1	6	17	78	\N	2026-08-24 22:59:44.680752	\N
327	ST-01-0327	شهد زياد	فاطمة	أنثى	يمني	مستمر	باقي	\N	2008-06-24	الحارة	الجنوبية	إب	\N	\N	\N	\N	1	6	17	88	\N	2026-08-24 22:59:44.680752	\N
328	ST-01-0328	نورة عبدالله	رنا	أنثى	يمني	مستمر	باقي	\N	2015-06-23	القرية	الجنوبية	تعز	\N	\N	\N	\N	1	6	18	95	\N	2026-08-24 22:59:44.680752	\N
329	ST-01-0329	عاصم عمر	خديجة	ذكر	يمني	مستمر	محول	\N	2018-01-09	المنطقة	الجنوبية	صنعاء	\N	\N	\N	\N	1	6	18	22	\N	2026-08-24 22:59:44.680752	\N
330	ST-01-0330	قيس مالك	رنا	ذكر	يمني	مستمر	باقي	\N	2008-03-06	الشارع	الشمالية	الحديدة	\N	\N	\N	\N	1	6	18	30	\N	2026-08-24 22:59:44.680752	\N
331	ST-01-0331	سلمى طلال	تقى	أنثى	يمني	مستمر	باقي	\N	2010-07-22	القرية	المدينة	تعز	\N	\N	\N	\N	1	6	18	96	\N	2026-08-24 22:59:44.680752	\N
332	ST-01-0332	حنان علي	شهد	أنثى	يمني	انسحاب	باقي	\N	2012-12-01	القرية	المركز	حضرموت	\N	\N	\N	\N	1	6	18	97	\N	2026-08-24 22:59:44.680752	\N
333	ST-01-0333	لينا إبراهيم	زينب	أنثى	يمني	مستمر	مستجد	\N	2009-10-01	القرية	المركز	صنعاء	\N	\N	\N	\N	1	6	18	79	\N	2026-08-24 22:59:44.680752	\N
334	ST-01-0334	عائشة محمد	أمل	أنثى	يمني	مستمر	باقي	\N	2015-12-15	الشارع	الشرقية	صنعاء	\N	\N	\N	\N	1	6	18	52	\N	2026-08-24 22:59:44.680752	\N
335	ST-01-0335	حسن يوسف	غادة	ذكر	يمني	مستمر	مستجد	\N	2018-10-09	الشارع	الشرقية	إب	\N	\N	\N	\N	1	6	18	95	\N	2026-08-24 22:59:44.680752	\N
336	ST-01-0336	لؤي سامر	تقى	ذكر	يمني	مستمر	مستجد	\N	2009-03-22	المنطقة	المدينة	حضرموت	\N	\N	\N	\N	1	6	18	17	\N	2026-08-24 22:59:44.680752	\N
337	ST-01-0337	فاطمة علي	فاطمة	أنثى	يمني	مستمر	مستجد	\N	2008-12-07	القرية	الشمالية	حضرموت	\N	\N	\N	\N	1	6	18	15	\N	2026-08-24 22:59:44.680752	\N
338	ST-01-0338	طلال ناصر	غادة	ذكر	يمني	مستمر	مستجد	\N	2016-05-10	المنطقة	الجنوبية	عدن	\N	\N	\N	\N	1	6	18	57	\N	2026-08-24 22:59:44.680752	\N
339	ST-01-0339	حمزة علي	عائشة	ذكر	يمني	انسحاب	مستجد	\N	2016-03-06	الحي	الشمالية	تعز	\N	\N	\N	\N	1	6	18	77	\N	2026-08-24 22:59:44.680752	\N
340	ST-01-0340	بلال أحمد	تقى	ذكر	يمني	مستمر	باقي	\N	2016-01-10	الحي	المركز	صنعاء	\N	\N	\N	\N	1	6	18	27	\N	2026-08-24 22:59:44.680752	\N
341	ST-01-0341	رحمة فهد	حنان	أنثى	يمني	مستمر	مستجد	\N	2007-09-28	القرية	المدينة	عدن	\N	\N	\N	\N	1	6	18	95	\N	2026-08-24 22:59:44.680752	\N
342	ST-01-0342	نجلاء خالد	غادة	أنثى	يمني	مستمر	باقي	\N	2013-03-22	الشارع	المركز	الحديدة	\N	\N	\N	\N	1	6	18	32	\N	2026-08-24 22:59:44.680752	\N
343	ST-01-0343	لينا إبراهيم	قمر	أنثى	يمني	مستمر	باقي	\N	2012-11-19	المنطقة	الشمالية	صنعاء	\N	\N	\N	\N	1	6	18	15	\N	2026-08-24 22:59:44.680752	\N
344	ST-01-0344	بلال أحمد	لينا	ذكر	يمني	مستمر	باقي	\N	2012-12-20	القرية	الشرقية	حضرموت	\N	\N	\N	\N	1	6	18	46	\N	2026-08-24 22:59:44.680752	\N
345	ST-01-0345	حمزة علي	سلمى	ذكر	يمني	مستمر	محول	\N	2011-09-26	القرية	الغربية	ذمار	\N	\N	\N	\N	1	6	18	22	\N	2026-08-24 22:59:44.680752	\N
346	ST-01-0346	سارة خالد	رحمة	أنثى	يمني	انسحاب	محول	\N	2016-08-26	الحارة	المدينة	تعز	\N	\N	\N	\N	1	6	18	74	\N	2026-08-24 22:59:44.680752	\N
347	ST-01-0347	هدى سامي	غادة	أنثى	يمني	مستمر	مستجد	\N	2011-12-05	الحارة	الشمالية	ذمار	\N	\N	\N	\N	1	6	18	64	\N	2026-08-24 22:59:44.680752	\N
348	ST-01-0348	سارة خالد	مريم	أنثى	يمني	مستمر	محول	\N	2016-03-27	الحي	المدينة	إب	\N	\N	\N	\N	1	6	18	89	\N	2026-08-24 22:59:44.680752	\N
349	ST-01-0349	قمر علي	جنات	أنثى	يمني	مستمر	مستجد	\N	2012-08-25	القرية	الغربية	حضرموت	\N	\N	\N	\N	1	7	19	95	\N	2026-08-24 22:59:44.680752	\N
350	ST-01-0350	فهد سعود	تقى	ذكر	يمني	مستمر	باقي	\N	2017-03-28	الحارة	المدينة	عدن	\N	\N	\N	\N	1	7	19	93	\N	2026-08-24 22:59:44.680752	\N
351	ST-01-0351	هاشم رائد	دينا	ذكر	يمني	مستمر	باقي	\N	2005-05-18	الشارع	المدينة	حضرموت	\N	\N	\N	\N	1	7	19	16	\N	2026-08-24 22:59:44.680752	\N
352	ST-01-0352	دينا حمد	جنات	أنثى	يمني	انسحاب	باقي	\N	2017-12-25	الشارع	الغربية	ذمار	\N	\N	\N	\N	1	7	19	94	\N	2026-08-24 22:59:44.680752	\N
353	ST-01-0353	آدم نوح	جنات	ذكر	يمني	مستمر	محول	\N	2013-04-17	الحي	المركز	تعز	\N	\N	\N	\N	1	7	19	81	\N	2026-08-24 22:59:44.680752	\N
354	ST-01-0354	قيس مالك	قمر	ذكر	يمني	انسحاب	مستجد	\N	2012-02-28	الحي	الشرقية	تعز	\N	\N	\N	\N	1	7	19	49	\N	2026-08-24 22:59:44.680752	\N
355	ST-01-0355	دينا حمد	قمر	أنثى	يمني	انسحاب	محول	\N	2005-12-28	المنطقة	الشرقية	ذمار	\N	\N	\N	\N	1	7	19	82	\N	2026-08-24 22:59:44.680752	\N
356	ST-01-0356	لؤي سامر	صفاء	ذكر	يمني	مستمر	باقي	\N	2005-10-11	الشارع	المدينة	ذمار	\N	\N	\N	\N	1	7	19	36	\N	2026-08-24 22:59:44.680752	\N
357	ST-01-0357	ماجد فهد	جنات	ذكر	يمني	مستمر	محول	\N	2009-12-06	الحارة	الشرقية	عدن	\N	\N	\N	\N	1	7	19	97	\N	2026-08-24 22:59:44.680752	\N
359	ST-01-0359	راشد علي	غادة	ذكر	يمني	مستمر	باقي	\N	2006-11-05	الحي	المركز	حضرموت	\N	\N	\N	\N	1	7	19	67	\N	2026-08-24 22:59:44.680752	\N
360	ST-01-0360	خديجة عمر	دينا	أنثى	يمني	مستمر	باقي	\N	2018-07-26	القرية	الشرقية	تعز	\N	\N	\N	\N	1	7	19	19	\N	2026-08-24 22:59:44.680752	\N
361	ST-01-0361	زينب حسن	لينا	أنثى	يمني	انسحاب	مستجد	\N	2011-02-18	المنطقة	الشمالية	ذمار	\N	\N	\N	\N	1	7	19	79	\N	2026-08-24 22:59:44.680752	\N
362	ST-01-0362	كرم نبيل	بسمة	ذكر	يمني	مستمر	مستجد	\N	2010-08-14	الحي	الغربية	المكلا	\N	\N	\N	\N	1	7	19	92	\N	2026-08-24 22:59:44.680752	\N
363	ST-01-0363	عاصم عمر	سلمى	ذكر	يمني	مستمر	باقي	\N	2009-02-20	الحي	الغربية	تعز	\N	\N	\N	\N	1	7	19	3	\N	2026-08-24 22:59:44.680752	\N
364	ST-01-0364	عاصم عمر	ضحى	ذكر	يمني	مستمر	مستجد	\N	2017-01-01	الحي	الغربية	تعز	\N	\N	\N	\N	1	7	19	39	\N	2026-08-24 22:59:44.680752	\N
365	ST-01-0365	أنس محمد	دينا	ذكر	يمني	انسحاب	باقي	\N	2013-11-13	الشارع	المدينة	حضرموت	\N	\N	\N	\N	1	7	19	7	\N	2026-08-24 22:59:44.680752	\N
366	ST-01-0366	ضحى محمد	جنات	أنثى	يمني	مستمر	باقي	\N	2017-01-23	القرية	المدينة	عدن	\N	\N	\N	\N	1	7	19	13	\N	2026-08-24 22:59:44.680752	\N
367	ST-01-0367	زينب حسن	غادة	أنثى	يمني	مستمر	محول	\N	2009-11-10	المنطقة	الشمالية	تعز	\N	\N	\N	\N	1	7	19	76	\N	2026-08-24 22:59:44.680752	\N
368	ST-01-0368	عاصم عمر	عائشة	ذكر	يمني	انسحاب	باقي	\N	2011-06-12	الشارع	الجنوبية	المكلا	\N	\N	\N	\N	1	7	19	50	\N	2026-08-24 22:59:44.680752	\N
369	ST-01-0369	نجلاء خالد	ضحى	أنثى	يمني	مستمر	محول	\N	2005-12-13	القرية	الشرقية	صنعاء	\N	\N	\N	\N	1	7	19	51	\N	2026-08-24 22:59:44.680752	\N
370	ST-01-0370	أمل ناصر	فاطمة	أنثى	يمني	مستمر	مستجد	\N	2016-07-12	القرية	الشرقية	إب	\N	\N	\N	\N	1	7	19	100	\N	2026-08-24 22:59:44.680752	\N
371	ST-01-0371	يوسف إبراهيم	تقى	ذكر	يمني	انسحاب	باقي	\N	2018-06-17	الحارة	الشرقية	إب	\N	\N	\N	\N	1	7	20	93	\N	2026-08-24 22:59:44.680752	\N
372	ST-01-0372	هدى سامي	فرح	أنثى	يمني	مستمر	محول	\N	2008-05-14	الحارة	الغربية	إب	\N	\N	\N	\N	1	7	20	28	\N	2026-08-24 22:59:44.680752	\N
373	ST-01-0373	ضحى محمد	صفاء	أنثى	يمني	مستمر	باقي	\N	2005-09-04	الحارة	الشمالية	عدن	\N	\N	\N	\N	1	7	20	99	\N	2026-08-24 22:59:44.680752	\N
374	ST-01-0374	نورة عبدالله	رحمة	أنثى	يمني	مستمر	مستجد	\N	2018-08-22	القرية	المركز	الحديدة	\N	\N	\N	\N	1	7	20	45	\N	2026-08-24 22:59:44.680752	\N
375	ST-01-0375	طلال ناصر	مريم	ذكر	يمني	مستمر	محول	\N	2016-05-04	القرية	الجنوبية	ذمار	\N	\N	\N	\N	1	7	20	54	\N	2026-08-24 22:59:44.680752	\N
376	ST-01-0376	سعيد علي	رحمة	ذكر	يمني	مستمر	مستجد	\N	2013-09-07	القرية	الغربية	عدن	\N	\N	\N	\N	1	7	20	70	\N	2026-08-24 22:59:44.680752	\N
377	ST-01-0377	حنان علي	سارة	أنثى	يمني	مستمر	مستجد	\N	2017-10-07	الحي	الغربية	ذمار	\N	\N	\N	\N	1	7	20	18	\N	2026-08-24 22:59:44.680752	\N
379	ST-01-0379	ضحى محمد	خديجة	أنثى	يمني	مستمر	باقي	\N	2005-12-15	الشارع	المدينة	الحديدة	\N	\N	\N	\N	1	7	20	81	\N	2026-08-24 22:59:44.680752	\N
380	ST-01-0380	ضحى محمد	تقى	أنثى	يمني	مستمر	باقي	\N	2018-01-02	المنطقة	المركز	الحديدة	\N	\N	\N	\N	1	7	20	38	\N	2026-08-24 22:59:44.680752	\N
381	ST-01-0381	مازن هاني	فرح	ذكر	يمني	مستمر	باقي	\N	2014-09-25	المنطقة	الشمالية	الحديدة	\N	\N	\N	\N	1	7	20	58	\N	2026-08-24 22:59:44.680752	\N
382	ST-01-0382	أمل ناصر	ضحى	أنثى	يمني	انسحاب	باقي	\N	2006-08-08	الحي	الغربية	ذمار	\N	\N	\N	\N	1	7	20	30	\N	2026-08-24 22:59:44.680752	\N
383	ST-01-0383	وليد طلال	قمر	ذكر	يمني	مستمر	باقي	\N	2005-07-12	الشارع	المدينة	ذمار	\N	\N	\N	\N	1	7	20	97	\N	2026-08-24 22:59:44.680752	\N
385	ST-01-0385	غادة أحمد	بسمة	أنثى	يمني	مستمر	مستجد	\N	2013-09-03	الحي	المركز	المكلا	\N	\N	\N	\N	1	7	20	36	\N	2026-08-24 22:59:44.680752	\N
386	ST-01-0386	فهد سعود	رحمة	ذكر	يمني	مستمر	باقي	\N	2012-03-23	الشارع	الشمالية	تعز	\N	\N	\N	\N	1	7	21	14	\N	2026-08-24 22:59:44.680752	\N
387	ST-01-0387	محمد أحمد	دينا	ذكر	يمني	مستمر	باقي	\N	2008-11-22	الحي	الجنوبية	إب	\N	\N	\N	\N	1	7	21	12	\N	2026-08-24 22:59:44.680752	\N
388	ST-01-0388	وسن يوسف	حنان	أنثى	يمني	مستمر	مستجد	\N	2010-01-27	المنطقة	الجنوبية	صنعاء	\N	\N	\N	\N	1	7	21	67	\N	2026-08-24 22:59:44.680752	\N
389	ST-01-0389	خديجة عمر	غادة	أنثى	يمني	مستمر	باقي	\N	2014-10-21	الحي	الشمالية	تعز	\N	\N	\N	\N	1	7	21	63	\N	2026-08-24 22:59:44.680752	\N
390	ST-01-0390	طلال ناصر	فرح	ذكر	يمني	انسحاب	مستجد	\N	2011-08-09	المنطقة	المدينة	إب	\N	\N	\N	\N	1	7	21	63	\N	2026-08-24 22:59:44.680752	\N
391	ST-01-0391	علي حسن	بسمة	ذكر	يمني	مستمر	باقي	\N	2018-09-15	الشارع	الشرقية	تعز	\N	\N	\N	\N	1	7	21	33	\N	2026-08-24 22:59:44.680752	\N
393	ST-01-0393	بدر حمد	شهد	ذكر	يمني	مستمر	باقي	\N	2014-11-02	الحي	المركز	تعز	\N	\N	\N	\N	1	7	21	45	\N	2026-08-24 22:59:44.680752	\N
394	ST-01-0394	نجلاء خالد	تقى	أنثى	يمني	مستمر	محول	\N	2007-06-19	الشارع	الجنوبية	إب	\N	\N	\N	\N	1	7	21	7	\N	2026-08-24 22:59:44.680752	\N
395	ST-01-0395	فهد سعود	فاطمة	ذكر	يمني	مستمر	مستجد	\N	2011-04-27	المنطقة	المركز	الحديدة	\N	\N	\N	\N	1	7	21	59	\N	2026-08-24 22:59:44.680752	\N
396	ST-01-0396	حمزة علي	شهد	ذكر	يمني	مستمر	باقي	\N	2009-11-27	الحي	الشرقية	الحديدة	\N	\N	\N	\N	1	7	21	5	\N	2026-08-24 22:59:44.680752	\N
397	ST-01-0397	شهد زياد	عائشة	أنثى	يمني	مستمر	باقي	\N	2006-08-26	القرية	المدينة	حضرموت	\N	\N	\N	\N	1	7	21	99	\N	2026-08-24 22:59:44.680752	\N
398	ST-01-0398	كرم نبيل	غادة	ذكر	يمني	مستمر	مستجد	\N	2015-02-18	القرية	المدينة	إب	\N	\N	\N	\N	1	7	21	30	\N	2026-08-24 22:59:44.680752	\N
400	ST-01-0400	أكرم وجيه	سلمى	ذكر	يمني	مستمر	مستجد	\N	2007-08-24	القرية	الشمالية	ذمار	\N	\N	\N	\N	1	7	21	29	\N	2026-08-24 22:59:44.680752	\N
401	ST-01-0401	دينا حمد	تقى	أنثى	يمني	انسحاب	باقي	\N	2014-12-15	الشارع	الجنوبية	الحديدة	\N	\N	\N	\N	1	7	21	75	\N	2026-08-24 22:59:44.680752	\N
402	ST-01-0402	فاطمة علي	صفاء	أنثى	يمني	مستمر	محول	\N	2014-04-25	المنطقة	الشمالية	إب	\N	\N	\N	\N	1	7	21	47	\N	2026-08-24 22:59:44.680752	\N
403	ST-01-0403	زينب حسن	زينب	أنثى	يمني	مستمر	باقي	\N	2017-10-18	القرية	الشمالية	ذمار	\N	\N	\N	\N	1	7	21	32	\N	2026-08-24 22:59:44.680752	\N
404	ST-01-0404	بسمة فهد	قمر	أنثى	يمني	مستمر	باقي	\N	2009-10-19	القرية	الشمالية	المكلا	\N	\N	\N	\N	1	7	21	39	\N	2026-08-24 22:59:44.680752	\N
405	ST-01-0405	تقى سعود	سارة	أنثى	يمني	مستمر	باقي	\N	2007-04-09	المنطقة	المدينة	إب	\N	\N	\N	\N	1	7	21	90	\N	2026-08-24 22:59:44.680752	\N
406	ST-01-0406	هدى سامي	نورة	أنثى	يمني	مستمر	باقي	\N	2012-02-05	المنطقة	الشرقية	عدن	\N	\N	\N	\N	1	7	21	76	\N	2026-08-24 22:59:44.680752	\N
407	ST-01-0407	هاشم رائد	سارة	ذكر	يمني	انسحاب	محول	\N	2007-04-17	المنطقة	الغربية	عدن	\N	\N	\N	\N	1	8	22	30	\N	2026-08-24 22:59:44.680752	\N
408	ST-01-0408	هدى سامي	فاطمة	أنثى	يمني	مستمر	باقي	\N	2007-12-24	المنطقة	الجنوبية	عدن	\N	\N	\N	\N	1	8	22	21	\N	2026-08-24 22:59:44.680752	\N
409	ST-01-0409	ماجد فهد	فرح	ذكر	يمني	مستمر	باقي	\N	2016-02-06	الشارع	المدينة	ذمار	\N	\N	\N	\N	1	8	22	91	\N	2026-08-24 22:59:44.680752	\N
410	ST-01-0410	زينب حسن	رنا	أنثى	يمني	انسحاب	محول	\N	2005-12-02	الشارع	الغربية	المكلا	\N	\N	\N	\N	1	8	22	23	\N	2026-08-24 22:59:44.680752	\N
411	ST-01-0411	تميم خالد	تقى	ذكر	يمني	انسحاب	باقي	\N	2008-12-24	القرية	الشمالية	المكلا	\N	\N	\N	\N	1	8	22	10	\N	2026-08-24 22:59:44.680752	\N
412	ST-01-0412	نجلاء خالد	هدى	أنثى	يمني	مستمر	باقي	\N	2008-10-18	الشارع	الجنوبية	تعز	\N	\N	\N	\N	1	8	22	97	\N	2026-08-24 22:59:44.680752	\N
413	ST-01-0413	فرح خالد	غادة	أنثى	يمني	مستمر	محول	\N	2007-05-08	القرية	المدينة	ذمار	\N	\N	\N	\N	1	8	22	38	\N	2026-08-24 22:59:44.680752	\N
414	ST-01-0414	تقى سعود	فرح	أنثى	يمني	مستمر	محول	\N	2009-11-03	الحي	المدينة	حضرموت	\N	\N	\N	\N	1	8	22	28	\N	2026-08-24 22:59:44.680752	\N
415	ST-01-0415	مودة عمر	قمر	أنثى	يمني	مستمر	مستجد	\N	2013-11-19	الشارع	الجنوبية	تعز	\N	\N	\N	\N	1	8	22	61	\N	2026-08-24 22:59:44.680752	\N
416	ST-01-0416	أمل ناصر	أمل	أنثى	يمني	مستمر	باقي	\N	2013-09-01	الحي	الشمالية	إب	\N	\N	\N	\N	1	8	22	4	\N	2026-08-24 22:59:44.680752	\N
417	ST-01-0417	فاطمة علي	دينا	أنثى	يمني	مستمر	مستجد	\N	2018-11-04	الحارة	المركز	صنعاء	\N	\N	\N	\N	1	8	22	79	\N	2026-08-24 22:59:44.680752	\N
418	ST-01-0418	سلمى طلال	ضحى	أنثى	يمني	مستمر	مستجد	\N	2013-12-18	الشارع	المدينة	الحديدة	\N	\N	\N	\N	1	8	22	42	\N	2026-08-24 22:59:44.680752	\N
419	ST-01-0419	زكريا يحيى	خديجة	ذكر	يمني	مستمر	مستجد	\N	2015-03-16	الحارة	الجنوبية	ذمار	\N	\N	\N	\N	1	8	22	16	\N	2026-08-24 22:59:44.680752	\N
420	ST-01-0420	ياسمين إبراهيم	هدى	أنثى	يمني	مستمر	باقي	\N	2012-01-01	الشارع	الشمالية	تعز	\N	\N	\N	\N	1	8	22	3	\N	2026-08-24 22:59:44.680752	\N
421	ST-01-0421	حسن يوسف	رحمة	ذكر	يمني	انسحاب	باقي	\N	2010-04-20	المنطقة	الشرقية	المكلا	\N	\N	\N	\N	1	8	22	4	\N	2026-08-24 22:59:44.680752	\N
422	ST-01-0422	عائشة محمد	زينب	أنثى	يمني	مستمر	باقي	\N	2017-05-04	الشارع	المركز	الحديدة	\N	\N	\N	\N	1	8	23	89	\N	2026-08-24 22:59:44.680752	\N
423	ST-01-0423	حمزة علي	مريم	ذكر	يمني	مستمر	باقي	\N	2014-10-10	القرية	المركز	تعز	\N	\N	\N	\N	1	8	23	68	\N	2026-08-24 22:59:44.680752	\N
424	ST-01-0424	محمد أحمد	ضحى	ذكر	يمني	مستمر	مستجد	\N	2010-01-17	الحارة	الغربية	عدن	\N	\N	\N	\N	1	8	23	34	\N	2026-08-24 22:59:44.680752	\N
425	ST-01-0425	نضال فؤاد	ضحى	ذكر	يمني	مستمر	مستجد	\N	2009-12-05	القرية	الجنوبية	إب	\N	\N	\N	\N	1	8	23	34	\N	2026-08-24 22:59:44.680752	\N
426	ST-01-0426	سلطان محمد	صفاء	ذكر	يمني	انسحاب	محول	\N	2008-02-16	الحي	الشمالية	المكلا	\N	\N	\N	\N	1	8	23	18	\N	2026-08-24 22:59:44.680752	\N
427	ST-01-0427	فرح خالد	ضحى	أنثى	يمني	مستمر	باقي	\N	2006-01-27	الحارة	الشرقية	تعز	\N	\N	\N	\N	1	8	23	81	\N	2026-08-24 22:59:44.680752	\N
428	ST-01-0428	فهد سعود	نورة	ذكر	يمني	مستمر	باقي	\N	2005-11-22	القرية	الشرقية	المكلا	\N	\N	\N	\N	1	8	23	5	\N	2026-08-24 22:59:44.680752	\N
429	ST-01-0429	علي حسن	دينا	ذكر	يمني	مستمر	باقي	\N	2017-06-22	الحي	الغربية	تعز	\N	\N	\N	\N	1	8	23	55	\N	2026-08-24 22:59:44.680752	\N
430	ST-01-0430	سعيد علي	دينا	ذكر	يمني	مستمر	باقي	\N	2006-04-24	المنطقة	المدينة	حضرموت	\N	\N	\N	\N	1	8	23	39	\N	2026-08-24 22:59:44.680752	\N
431	ST-01-0431	حنان علي	صفاء	أنثى	يمني	مستمر	باقي	\N	2015-06-07	الشارع	المدينة	إب	\N	\N	\N	\N	1	8	23	72	\N	2026-08-24 22:59:44.680752	\N
432	ST-01-0432	نورة عبدالله	أمل	أنثى	يمني	مستمر	مستجد	\N	2014-10-27	المنطقة	الشمالية	ذمار	\N	\N	\N	\N	1	8	23	66	\N	2026-08-24 22:59:44.680752	\N
433	ST-01-0433	محمد أحمد	دينا	ذكر	يمني	مستمر	محول	\N	2005-04-13	الحارة	الشرقية	ذمار	\N	\N	\N	\N	1	8	23	32	\N	2026-08-24 22:59:44.680752	\N
434	ST-01-0434	آدم نوح	حنان	ذكر	يمني	مستمر	باقي	\N	2010-11-14	الحارة	المركز	عدن	\N	\N	\N	\N	1	8	23	85	\N	2026-08-24 22:59:44.680752	\N
435	ST-01-0435	وسن يوسف	لينا	أنثى	يمني	مستمر	محول	\N	2018-03-13	الشارع	الشمالية	ذمار	\N	\N	\N	\N	1	8	23	67	\N	2026-08-24 22:59:44.680752	\N
436	ST-01-0436	أمل ناصر	فاطمة	أنثى	يمني	مستمر	محول	\N	2015-01-03	الحي	الغربية	ذمار	\N	\N	\N	\N	1	8	23	9	\N	2026-08-24 22:59:44.680752	\N
437	ST-01-0437	خالد عبدالله	دينا	ذكر	يمني	انسحاب	محول	\N	2018-11-02	القرية	الجنوبية	المكلا	\N	\N	\N	\N	1	8	23	54	\N	2026-08-24 22:59:44.680752	\N
438	ST-01-0438	نورة عبدالله	ضحى	أنثى	يمني	مستمر	باقي	\N	2014-07-12	القرية	المركز	المكلا	\N	\N	\N	\N	1	8	23	28	\N	2026-08-24 22:59:44.680752	\N
439	ST-01-0439	تميم خالد	فاطمة	ذكر	يمني	مستمر	محول	\N	2005-03-11	الشارع	الشرقية	المكلا	\N	\N	\N	\N	1	8	23	37	\N	2026-08-24 22:59:44.680752	\N
440	ST-01-0440	يحيى عادل	مريم	ذكر	يمني	مستمر	محول	\N	2008-11-20	الحارة	الشرقية	تعز	\N	\N	\N	\N	1	8	23	83	\N	2026-08-24 22:59:44.680752	\N
441	ST-01-0441	وائل سامي	زينب	ذكر	يمني	مستمر	محول	\N	2006-05-15	الشارع	الشرقية	المكلا	\N	\N	\N	\N	1	8	23	75	\N	2026-08-24 22:59:44.680752	\N
443	ST-01-0443	صفاء هشام	بسمة	أنثى	يمني	مستمر	باقي	\N	2015-03-18	المنطقة	الجنوبية	المكلا	\N	\N	\N	\N	1	8	24	25	\N	2026-08-24 22:59:44.680752	\N
444	ST-01-0444	غادة أحمد	رنا	أنثى	يمني	مستمر	باقي	\N	2016-12-18	الحارة	الشرقية	المكلا	\N	\N	\N	\N	1	8	24	45	\N	2026-08-24 22:59:44.680752	\N
445	ST-01-0445	وائل سامي	ضحى	ذكر	يمني	انسحاب	باقي	\N	2005-10-27	الشارع	المدينة	ذمار	\N	\N	\N	\N	1	8	24	15	\N	2026-08-24 22:59:44.680752	\N
446	ST-01-0446	عائشة محمد	جنات	أنثى	يمني	مستمر	باقي	\N	2011-07-19	الحارة	المركز	ذمار	\N	\N	\N	\N	1	8	24	6	\N	2026-08-24 22:59:44.680752	\N
447	ST-01-0447	لمى حسن	غادة	أنثى	يمني	مستمر	محول	\N	2016-01-27	الحي	المركز	صنعاء	\N	\N	\N	\N	1	8	24	63	\N	2026-08-24 22:59:44.680752	\N
448	ST-01-0448	يحيى عادل	أمل	ذكر	يمني	انسحاب	مستجد	\N	2017-07-25	الشارع	الشمالية	ذمار	\N	\N	\N	\N	1	8	24	69	\N	2026-08-24 22:59:44.680752	\N
449	ST-01-0449	سارة خالد	جنات	أنثى	يمني	انسحاب	باقي	\N	2016-12-13	الشارع	الشرقية	عدن	\N	\N	\N	\N	1	8	24	97	\N	2026-08-24 22:59:44.680752	\N
450	ST-01-0450	سعيد علي	أمل	ذكر	يمني	مستمر	باقي	\N	2006-03-28	القرية	الشرقية	إب	\N	\N	\N	\N	1	8	24	95	\N	2026-08-24 22:59:44.680752	\N
451	ST-01-0451	مريم أحمد	دينا	أنثى	يمني	مستمر	باقي	\N	2009-10-26	القرية	الشرقية	المكلا	\N	\N	\N	\N	1	8	24	51	\N	2026-08-24 22:59:44.680752	\N
452	ST-01-0452	مودة عمر	خديجة	أنثى	يمني	مستمر	محول	\N	2015-07-03	الحارة	الشرقية	عدن	\N	\N	\N	\N	1	8	24	57	\N	2026-08-24 22:59:44.680752	\N
453	ST-01-0453	نورة عبدالله	رحمة	أنثى	يمني	مستمر	باقي	\N	2010-03-15	الحارة	المركز	المكلا	\N	\N	\N	\N	1	8	24	71	\N	2026-08-24 22:59:44.680752	\N
454	ST-01-0454	فارس خالد	رحمة	ذكر	يمني	مستمر	مستجد	\N	2012-12-16	الحي	الشمالية	المكلا	\N	\N	\N	\N	1	8	24	11	\N	2026-08-24 22:59:44.680752	\N
456	ST-01-0456	أنس محمد	ضحى	ذكر	يمني	انسحاب	باقي	\N	2016-03-28	المنطقة	الشمالية	صنعاء	\N	\N	\N	\N	1	8	24	25	\N	2026-08-24 22:59:44.680752	\N
457	ST-01-0457	ماجد فهد	ضحى	ذكر	يمني	مستمر	مستجد	\N	2017-09-27	المنطقة	الشمالية	إب	\N	\N	\N	\N	1	8	24	19	\N	2026-08-24 22:59:44.680752	\N
458	ST-01-0458	عائشة محمد	غادة	أنثى	يمني	مستمر	باقي	\N	2009-06-24	المنطقة	المركز	حضرموت	\N	\N	\N	\N	1	8	24	74	\N	2026-08-24 22:59:44.680752	\N
459	ST-01-0459	نورة عبدالله	رنا	أنثى	يمني	مستمر	باقي	\N	2005-10-12	المنطقة	الشرقية	الحديدة	\N	\N	\N	\N	1	8	24	31	\N	2026-08-24 22:59:44.680752	\N
460	ST-01-0460	نضال فؤاد	قمر	ذكر	يمني	مستمر	مستجد	\N	2016-04-24	الحارة	المركز	إب	\N	\N	\N	\N	1	8	24	4	\N	2026-08-24 22:59:44.680752	\N
461	ST-01-0461	سلمى طلال	زينب	أنثى	يمني	مستمر	باقي	\N	2018-06-28	المنطقة	المركز	عدن	\N	\N	\N	\N	1	8	24	95	\N	2026-08-24 22:59:44.680752	\N
462	ST-01-0462	وسن يوسف	رنا	أنثى	يمني	انسحاب	باقي	\N	2013-03-22	المنطقة	الشرقية	تعز	\N	\N	\N	\N	1	8	24	47	\N	2026-08-24 22:59:44.680752	\N
463	ST-01-0463	دينا حمد	عائشة	أنثى	يمني	انسحاب	باقي	\N	2012-06-19	الحارة	الجنوبية	المكلا	\N	\N	\N	\N	1	9	25	30	\N	2026-08-24 22:59:44.680752	\N
464	ST-01-0464	غادة أحمد	سلمى	أنثى	يمني	مستمر	باقي	\N	2013-11-09	الشارع	الغربية	عدن	\N	\N	\N	\N	1	9	25	7	\N	2026-08-24 22:59:44.680752	\N
465	ST-01-0465	لمى حسن	شهد	أنثى	يمني	مستمر	باقي	\N	2008-12-11	الحارة	الغربية	صنعاء	\N	\N	\N	\N	1	9	25	18	\N	2026-08-24 22:59:44.680752	\N
466	ST-01-0466	دينا حمد	نورة	أنثى	يمني	مستمر	باقي	\N	2012-08-28	الحي	المدينة	المكلا	\N	\N	\N	\N	1	9	25	39	\N	2026-08-24 22:59:44.680752	\N
467	ST-01-0467	تقى سعود	رنا	أنثى	يمني	مستمر	باقي	\N	2015-01-16	الحي	الغربية	عدن	\N	\N	\N	\N	1	9	25	58	\N	2026-08-24 22:59:44.680752	\N
468	ST-01-0468	علي حسن	رحمة	ذكر	يمني	انسحاب	محول	\N	2017-10-01	الشارع	المدينة	إب	\N	\N	\N	\N	1	9	25	94	\N	2026-08-24 22:59:44.680752	\N
469	ST-01-0469	بلال أحمد	فرح	ذكر	يمني	مستمر	باقي	\N	2009-03-11	المنطقة	المركز	الحديدة	\N	\N	\N	\N	1	9	25	83	\N	2026-08-24 22:59:44.680752	\N
470	ST-01-0470	نضال فؤاد	أمل	ذكر	يمني	مستمر	باقي	\N	2009-01-20	القرية	المدينة	تعز	\N	\N	\N	\N	1	9	25	80	\N	2026-08-24 22:59:44.680752	\N
471	ST-01-0471	وسن يوسف	سارة	أنثى	يمني	مستمر	باقي	\N	2018-12-19	القرية	الغربية	حضرموت	\N	\N	\N	\N	1	9	25	37	\N	2026-08-24 22:59:44.680752	\N
472	ST-01-0472	زياد هشام	سلمى	ذكر	يمني	انسحاب	باقي	\N	2014-02-21	الشارع	الغربية	عدن	\N	\N	\N	\N	1	9	25	38	\N	2026-08-24 22:59:44.680752	\N
473	ST-01-0473	لينا إبراهيم	جنات	أنثى	يمني	مستمر	باقي	\N	2014-01-21	الحارة	المدينة	تعز	\N	\N	\N	\N	1	9	25	41	\N	2026-08-24 22:59:44.680752	\N
474	ST-01-0474	عمر خالد	رنا	ذكر	يمني	انسحاب	باقي	\N	2008-02-12	المنطقة	المدينة	صنعاء	\N	\N	\N	\N	1	9	25	64	\N	2026-08-24 22:59:44.680752	\N
475	ST-01-0475	صالح إبراهيم	هدى	ذكر	يمني	مستمر	باقي	\N	2005-06-04	القرية	الشرقية	المكلا	\N	\N	\N	\N	1	9	25	28	\N	2026-08-24 22:59:44.680752	\N
476	ST-01-0476	نضال فؤاد	تقى	ذكر	يمني	مستمر	باقي	\N	2005-02-19	الحارة	المدينة	عدن	\N	\N	\N	\N	1	9	25	9	\N	2026-08-24 22:59:44.680752	\N
477	ST-01-0477	قيس مالك	زينب	ذكر	يمني	مستمر	باقي	\N	2016-01-24	المنطقة	المدينة	المكلا	\N	\N	\N	\N	1	9	25	42	\N	2026-08-24 22:59:44.680752	\N
478	ST-01-0478	مريم أحمد	حنان	أنثى	يمني	مستمر	باقي	\N	2018-04-06	الحارة	المركز	حضرموت	\N	\N	\N	\N	1	9	25	35	\N	2026-08-24 22:59:44.680752	\N
479	ST-01-0479	صالح إبراهيم	أمل	ذكر	يمني	مستمر	مستجد	\N	2007-05-25	الحي	الشرقية	إب	\N	\N	\N	\N	1	9	26	42	\N	2026-08-24 22:59:44.680752	\N
480	ST-01-0480	صفاء هشام	مريم	أنثى	يمني	مستمر	مستجد	\N	2009-01-20	الحارة	المدينة	ذمار	\N	\N	\N	\N	1	9	26	72	\N	2026-08-24 22:59:44.680752	\N
481	ST-01-0481	نجلاء خالد	مريم	أنثى	يمني	مستمر	باقي	\N	2018-03-11	الشارع	الجنوبية	عدن	\N	\N	\N	\N	1	9	26	87	\N	2026-08-24 22:59:44.680752	\N
482	ST-01-0482	نورة عبدالله	رنا	أنثى	يمني	مستمر	مستجد	\N	2012-12-06	المنطقة	الجنوبية	المكلا	\N	\N	\N	\N	1	9	26	4	\N	2026-08-24 22:59:44.680752	\N
483	ST-01-0483	هبة عبدالله	عائشة	أنثى	يمني	مستمر	محول	\N	2016-11-16	القرية	الجنوبية	الحديدة	\N	\N	\N	\N	1	9	26	52	\N	2026-08-24 22:59:44.680752	\N
484	ST-01-0484	مازن هاني	سارة	ذكر	يمني	مستمر	مستجد	\N	2011-11-09	الشارع	المركز	ذمار	\N	\N	\N	\N	1	9	26	93	\N	2026-08-24 22:59:44.680752	\N
485	ST-01-0485	سلمى طلال	جنات	أنثى	يمني	مستمر	محول	\N	2018-12-03	القرية	الجنوبية	صنعاء	\N	\N	\N	\N	1	9	26	11	\N	2026-08-24 22:59:44.680752	\N
486	ST-01-0486	هبة عبدالله	هدى	أنثى	يمني	مستمر	مستجد	\N	2006-12-15	الحي	الجنوبية	إب	\N	\N	\N	\N	1	9	26	50	\N	2026-08-24 22:59:44.680752	\N
487	ST-01-0487	هاشم رائد	أمل	ذكر	يمني	مستمر	محول	\N	2015-06-14	الحي	الشرقية	الحديدة	\N	\N	\N	\N	1	9	26	18	\N	2026-08-24 22:59:44.680752	\N
488	ST-01-0488	فاطمة علي	سلمى	أنثى	يمني	انسحاب	باقي	\N	2010-04-16	القرية	الجنوبية	الحديدة	\N	\N	\N	\N	1	9	26	63	\N	2026-08-24 22:59:44.680752	\N
489	ST-01-0489	جنات محمد	رنا	أنثى	يمني	مستمر	باقي	\N	2011-01-18	الشارع	المركز	الحديدة	\N	\N	\N	\N	1	9	26	97	\N	2026-08-24 22:59:44.680752	\N
490	ST-01-0490	كرم نبيل	عائشة	ذكر	يمني	مستمر	باقي	\N	2010-11-02	الحارة	الجنوبية	الحديدة	\N	\N	\N	\N	1	9	26	56	\N	2026-08-24 22:59:44.680752	\N
491	ST-01-0491	بسمة فهد	رحمة	أنثى	يمني	مستمر	باقي	\N	2010-12-11	المنطقة	المدينة	المكلا	\N	\N	\N	\N	1	9	26	5	\N	2026-08-24 22:59:44.680752	\N
492	ST-01-0492	لمى حسن	خديجة	أنثى	يمني	مستمر	باقي	\N	2012-10-10	المنطقة	الشرقية	ذمار	\N	\N	\N	\N	1	9	26	6	\N	2026-08-24 22:59:44.680752	\N
493	ST-01-0493	قمر علي	هدى	أنثى	يمني	مستمر	مستجد	\N	2012-07-23	الشارع	المركز	إب	\N	\N	\N	\N	1	9	26	55	\N	2026-08-24 22:59:44.680752	\N
494	ST-01-0494	رنا يوسف	فرح	أنثى	يمني	مستمر	محول	\N	2006-08-10	القرية	الجنوبية	عدن	\N	\N	\N	\N	1	9	26	22	\N	2026-08-24 22:59:44.680752	\N
495	ST-01-0495	سلطان محمد	عائشة	ذكر	يمني	انسحاب	محول	\N	2012-04-20	الشارع	الجنوبية	عدن	\N	\N	\N	\N	1	9	26	52	\N	2026-08-24 22:59:44.680752	\N
496	ST-01-0496	ضحى محمد	سارة	أنثى	يمني	مستمر	باقي	\N	2015-02-18	القرية	المدينة	المكلا	\N	\N	\N	\N	1	9	26	50	\N	2026-08-24 22:59:44.680752	\N
497	ST-01-0497	قمر علي	خديجة	أنثى	يمني	مستمر	باقي	\N	2018-09-17	الحي	الجنوبية	ذمار	\N	\N	\N	\N	1	9	26	50	\N	2026-08-24 22:59:44.680752	\N
498	ST-01-0498	طلال ناصر	فاطمة	ذكر	يمني	مستمر	باقي	\N	2010-03-02	الشارع	الشمالية	تعز	\N	\N	\N	\N	1	9	26	83	\N	2026-08-24 22:59:44.680752	\N
499	ST-01-0499	هدى سامي	صفاء	أنثى	يمني	انسحاب	محول	\N	2016-02-27	الحارة	المدينة	الحديدة	\N	\N	\N	\N	1	9	26	59	\N	2026-08-24 22:59:44.680752	\N
500	ST-01-0500	عاصم عمر	تقى	ذكر	يمني	مستمر	باقي	\N	2009-12-14	القرية	الشمالية	ذمار	\N	\N	\N	\N	1	9	27	83	\N	2026-08-24 22:59:44.680752	\N
501	ST-01-0501	وليد طلال	لينا	ذكر	يمني	مستمر	باقي	\N	2016-08-17	الحارة	الشمالية	حضرموت	\N	\N	\N	\N	1	9	27	37	\N	2026-08-24 22:59:44.680752	\N
502	ST-01-0502	وائل سامي	لينا	ذكر	يمني	مستمر	باقي	\N	2018-11-06	الحي	الشرقية	ذمار	\N	\N	\N	\N	1	9	27	42	\N	2026-08-24 22:59:44.680752	\N
503	ST-01-0503	بسمة فهد	هدى	أنثى	يمني	مستمر	مستجد	\N	2010-09-06	الحي	الشمالية	حضرموت	\N	\N	\N	\N	1	9	27	43	\N	2026-08-24 22:59:44.680752	\N
504	ST-01-0504	رحمة فهد	هدى	أنثى	يمني	مستمر	باقي	\N	2016-11-17	القرية	الجنوبية	عدن	\N	\N	\N	\N	1	9	27	81	\N	2026-08-24 22:59:44.680752	\N
505	ST-01-0505	عاصم عمر	صفاء	ذكر	يمني	مستمر	مستجد	\N	2006-01-21	الحارة	الغربية	الحديدة	\N	\N	\N	\N	1	9	27	52	\N	2026-08-24 22:59:44.680752	\N
507	ST-01-0507	لؤي سامر	قمر	ذكر	يمني	مستمر	محول	\N	2006-04-28	القرية	المركز	إب	\N	\N	\N	\N	1	9	27	10	\N	2026-08-24 22:59:44.680752	\N
508	ST-01-0508	يوسف إبراهيم	نورة	ذكر	يمني	مستمر	مستجد	\N	2008-08-19	القرية	الشرقية	تعز	\N	\N	\N	\N	1	9	27	59	\N	2026-08-24 22:59:44.680752	\N
509	ST-01-0509	دينا حمد	فرح	أنثى	يمني	مستمر	محول	\N	2018-01-05	الحارة	المدينة	تعز	\N	\N	\N	\N	1	9	27	91	\N	2026-08-24 22:59:44.680752	\N
510	ST-01-0510	سلمى طلال	أمل	أنثى	يمني	مستمر	باقي	\N	2015-07-15	الحارة	الجنوبية	صنعاء	\N	\N	\N	\N	1	9	27	32	\N	2026-08-24 22:59:44.680752	\N
511	ST-01-0511	بسمة فهد	فاطمة	أنثى	يمني	مستمر	مستجد	\N	2006-03-10	الحي	المدينة	ذمار	\N	\N	\N	\N	1	9	27	17	\N	2026-08-24 22:59:44.680752	\N
512	ST-01-0512	ياسمين إبراهيم	غادة	أنثى	يمني	مستمر	باقي	\N	2012-06-01	الحارة	الشمالية	حضرموت	\N	\N	\N	\N	1	9	27	49	\N	2026-08-24 22:59:44.680752	\N
513	ST-01-0513	قمر علي	فاطمة	أنثى	يمني	انسحاب	محول	\N	2007-06-20	الحارة	الغربية	الحديدة	\N	\N	\N	\N	1	9	27	39	\N	2026-08-24 22:59:44.680752	\N
514	ST-01-0514	قيس مالك	خديجة	ذكر	يمني	مستمر	محول	\N	2013-12-06	الحارة	الغربية	تعز	\N	\N	\N	\N	1	9	27	5	\N	2026-08-24 22:59:44.680752	\N
515	ST-01-0515	أكرم وجيه	تقى	ذكر	يمني	انسحاب	مستجد	\N	2018-12-05	القرية	المدينة	صنعاء	\N	\N	\N	\N	1	9	27	28	\N	2026-08-24 22:59:44.680752	\N
516	ST-01-0516	رحمة فهد	فرح	أنثى	يمني	مستمر	مستجد	\N	2015-01-15	الحارة	الشمالية	تعز	\N	\N	\N	\N	1	9	27	72	\N	2026-08-24 22:59:44.680752	\N
517	ST-01-0517	عمر خالد	لينا	ذكر	يمني	مستمر	باقي	\N	2009-05-18	المنطقة	الشمالية	ذمار	\N	\N	\N	\N	1	9	27	24	\N	2026-08-24 22:59:44.680752	\N
518	ST-01-0518	عمر خالد	خديجة	ذكر	يمني	مستمر	محول	\N	2018-02-09	القرية	الغربية	الحديدة	\N	\N	\N	\N	1	9	27	27	\N	2026-08-24 22:59:44.680752	\N
519	ST-01-0519	نورة عبدالله	حنان	أنثى	يمني	مستمر	باقي	\N	2013-08-02	الحارة	المدينة	المكلا	\N	\N	\N	\N	1	9	27	59	\N	2026-08-24 22:59:44.680752	\N
520	ST-01-0520	حمزة علي	سارة	ذكر	يمني	مستمر	باقي	\N	2015-01-13	الشارع	المدينة	إب	\N	\N	\N	\N	1	9	27	94	\N	2026-08-24 22:59:44.680752	\N
521	ST-01-0521	بلال أحمد	بسمة	ذكر	يمني	مستمر	باقي	\N	2010-07-16	المنطقة	المركز	المكلا	\N	\N	\N	\N	1	9	27	65	\N	2026-08-24 22:59:44.680752	\N
522	ST-01-0522	لمى حسن	بسمة	أنثى	يمني	مستمر	محول	\N	2015-08-24	الحي	الشرقية	ذمار	\N	\N	\N	\N	1	10	\N	26	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
575	ST-01-0575	وسن يوسف	شهد	أنثى	يمني	مستمر	مستجد	\N	2014-11-03	القرية	المدينة	المكلا	\N	\N	\N	\N	1	11	31	90	\N	2026-08-24 22:59:44.680752	\N
576	ST-01-0576	لينا إبراهيم	تقى	أنثى	يمني	مستمر	مستجد	\N	2005-04-23	الحارة	الشرقية	عدن	\N	\N	\N	\N	1	11	31	56	\N	2026-08-24 22:59:44.680752	\N
577	ST-01-0577	هدى سامي	أمل	أنثى	يمني	انسحاب	محول	\N	2011-06-13	القرية	الغربية	صنعاء	\N	\N	\N	\N	1	11	31	16	\N	2026-08-24 22:59:44.680752	\N
578	ST-01-0578	صفاء هشام	صفاء	أنثى	يمني	انسحاب	مستجد	\N	2005-11-05	الشارع	المدينة	صنعاء	\N	\N	\N	\N	1	11	31	54	\N	2026-08-24 22:59:44.680752	\N
579	ST-01-0579	مودة عمر	ضحى	أنثى	يمني	مستمر	باقي	\N	2013-05-22	القرية	المدينة	الحديدة	\N	\N	\N	\N	1	11	31	96	\N	2026-08-24 22:59:44.680752	\N
580	ST-01-0580	نجلاء خالد	غادة	أنثى	يمني	مستمر	باقي	\N	2010-07-13	الشارع	المركز	الحديدة	\N	\N	\N	\N	1	11	31	11	\N	2026-08-24 22:59:44.680752	\N
581	ST-01-0581	قمر علي	جنات	أنثى	يمني	مستمر	باقي	\N	2014-09-10	الحارة	الغربية	المكلا	\N	\N	\N	\N	1	11	31	45	\N	2026-08-24 22:59:44.680752	\N
582	ST-01-0582	آدم نوح	شهد	ذكر	يمني	مستمر	مستجد	\N	2012-03-20	الشارع	الغربية	عدن	\N	\N	\N	\N	1	11	31	62	\N	2026-08-24 22:59:44.680752	\N
583	ST-01-0583	يوسف إبراهيم	نورة	ذكر	يمني	انسحاب	باقي	\N	2011-01-24	الشارع	المدينة	الحديدة	\N	\N	\N	\N	1	11	31	84	\N	2026-08-24 22:59:44.680752	\N
584	ST-01-0584	وسن يوسف	رحمة	أنثى	يمني	مستمر	باقي	\N	2011-04-11	الحي	الجنوبية	المكلا	\N	\N	\N	\N	1	11	31	61	\N	2026-08-24 22:59:44.680752	\N
585	ST-01-0585	شهد زياد	تقى	أنثى	يمني	انسحاب	باقي	\N	2007-05-27	الحي	المركز	إب	\N	\N	\N	\N	1	11	31	15	\N	2026-08-24 22:59:44.680752	\N
586	ST-01-0586	لمى حسن	خديجة	أنثى	يمني	مستمر	مستجد	\N	2018-09-02	الحارة	الجنوبية	إب	\N	\N	\N	\N	1	11	31	5	\N	2026-08-24 22:59:44.680752	\N
588	ST-01-0588	ناصر عبدالعزيز	أمل	ذكر	يمني	مستمر	محول	\N	2018-05-01	الحي	الجنوبية	عدن	\N	\N	\N	\N	1	11	31	65	\N	2026-08-24 22:59:44.680752	\N
589	ST-01-0589	مريم أحمد	قمر	أنثى	يمني	انسحاب	محول	\N	2014-12-23	القرية	الغربية	تعز	\N	\N	\N	\N	1	11	31	60	\N	2026-08-24 22:59:44.680752	\N
590	ST-01-0590	نجلاء خالد	دينا	أنثى	يمني	انسحاب	مستجد	\N	2005-11-18	القرية	الغربية	الحديدة	\N	\N	\N	\N	1	11	31	53	\N	2026-08-24 22:59:44.680752	\N
591	ST-01-0591	جنات محمد	خديجة	أنثى	يمني	مستمر	باقي	\N	2006-11-26	الحارة	الغربية	إب	\N	\N	\N	\N	1	11	31	89	\N	2026-08-24 22:59:44.680752	\N
592	ST-01-0592	محمد أحمد	جنات	ذكر	يمني	مستمر	محول	\N	2007-03-21	الشارع	المدينة	ذمار	\N	\N	\N	\N	1	11	31	82	\N	2026-08-24 22:59:44.680752	\N
593	ST-01-0593	بسمة فهد	زينب	أنثى	يمني	مستمر	محول	\N	2016-01-05	القرية	الجنوبية	تعز	\N	\N	\N	\N	1	11	31	11	\N	2026-08-24 22:59:44.680752	\N
594	ST-01-0594	نورة عبدالله	رنا	أنثى	يمني	مستمر	باقي	\N	2010-09-28	المنطقة	المركز	عدن	\N	\N	\N	\N	1	11	31	89	\N	2026-08-24 22:59:44.680752	\N
595	ST-01-0595	حسن يوسف	دينا	ذكر	يمني	مستمر	محول	\N	2008-04-15	الحي	المدينة	إب	\N	\N	\N	\N	1	11	31	20	\N	2026-08-24 22:59:44.680752	\N
596	ST-01-0596	فرح خالد	عائشة	أنثى	يمني	مستمر	باقي	\N	2009-02-09	القرية	الشمالية	المكلا	\N	\N	\N	\N	1	11	31	15	\N	2026-08-24 22:59:44.680752	\N
597	ST-01-0597	ماجد فهد	زينب	ذكر	يمني	انسحاب	باقي	\N	2009-06-23	القرية	المركز	إب	\N	\N	\N	\N	1	11	31	59	\N	2026-08-24 22:59:44.680752	\N
598	ST-01-0598	ماجد فهد	عائشة	ذكر	يمني	مستمر	محول	\N	2014-01-22	الحي	الغربية	حضرموت	\N	\N	\N	\N	1	11	32	67	\N	2026-08-24 22:59:44.680752	\N
599	ST-01-0599	شهد زياد	تقى	أنثى	يمني	مستمر	مستجد	\N	2012-12-06	المنطقة	الغربية	صنعاء	\N	\N	\N	\N	1	11	32	8	\N	2026-08-24 22:59:44.680752	\N
600	ST-01-0600	نجلاء خالد	جنات	أنثى	يمني	مستمر	محول	\N	2017-02-07	القرية	الشمالية	ذمار	\N	\N	\N	\N	1	11	32	83	\N	2026-08-24 22:59:44.680752	\N
601	ST-01-0601	وائل سامي	هدى	ذكر	يمني	مستمر	مستجد	\N	2006-02-04	الشارع	الجنوبية	الحديدة	\N	\N	\N	\N	1	11	32	63	\N	2026-08-24 22:59:44.680752	\N
602	ST-01-0602	صفاء هشام	مريم	أنثى	يمني	انسحاب	مستجد	\N	2009-08-03	الشارع	المدينة	الحديدة	\N	\N	\N	\N	1	11	32	10	\N	2026-08-24 22:59:44.680752	\N
603	ST-01-0603	عمر خالد	فاطمة	ذكر	يمني	مستمر	باقي	\N	2011-01-17	المنطقة	المدينة	إب	\N	\N	\N	\N	1	11	32	28	\N	2026-08-24 22:59:44.680752	\N
604	ST-01-0604	زكريا يحيى	أمل	ذكر	يمني	مستمر	مستجد	\N	2008-05-14	المنطقة	الشمالية	عدن	\N	\N	\N	\N	1	11	32	27	\N	2026-08-24 22:59:44.680752	\N
605	ST-01-0605	رنا يوسف	غادة	أنثى	يمني	مستمر	باقي	\N	2015-04-08	المنطقة	الشمالية	الحديدة	\N	\N	\N	\N	1	11	32	57	\N	2026-08-24 22:59:44.680752	\N
606	ST-01-0606	مريم أحمد	جنات	أنثى	يمني	مستمر	محول	\N	2005-11-11	الحي	المدينة	حضرموت	\N	\N	\N	\N	1	11	32	33	\N	2026-08-24 22:59:44.680752	\N
607	ST-01-0607	شهد زياد	ضحى	أنثى	يمني	مستمر	مستجد	\N	2012-09-11	الشارع	الغربية	صنعاء	\N	\N	\N	\N	1	11	32	53	\N	2026-08-24 22:59:44.680752	\N
565	ST-01-0565	ياسمين إبراهيم	مريم	أنثى	يمني	مستمر	باقي	\N	2010-06-25	المنطقة	الشمالية	تعز	\N	\N	\N	\N	1	10	\N	58	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
608	ST-01-0608	شهد زياد	بسمة	أنثى	يمني	مستمر	محول	\N	2008-05-02	المنطقة	المدينة	عدن	\N	\N	\N	\N	1	11	32	95	\N	2026-08-24 22:59:44.680752	\N
609	ST-01-0609	مريم أحمد	بسمة	أنثى	يمني	مستمر	مستجد	\N	2008-02-13	القرية	الشمالية	حضرموت	\N	\N	\N	\N	1	11	32	82	\N	2026-08-24 22:59:44.680752	\N
610	ST-01-0610	شهد زياد	غادة	أنثى	يمني	انسحاب	باقي	\N	2016-06-17	الحارة	الجنوبية	حضرموت	\N	\N	\N	\N	1	11	32	48	\N	2026-08-24 22:59:44.680752	\N
611	ST-01-0611	صالح إبراهيم	سلمى	ذكر	يمني	مستمر	محول	\N	2012-02-06	الحي	الشرقية	المكلا	\N	\N	\N	\N	1	11	32	5	\N	2026-08-24 22:59:44.680752	\N
612	ST-01-0612	يوسف إبراهيم	فاطمة	ذكر	يمني	انسحاب	مستجد	\N	2017-04-19	الحارة	الجنوبية	المكلا	\N	\N	\N	\N	1	11	32	13	\N	2026-08-24 22:59:44.680752	\N
613	ST-01-0613	فرح خالد	دينا	أنثى	يمني	مستمر	باقي	\N	2007-05-27	المنطقة	المركز	تعز	\N	\N	\N	\N	1	11	32	70	\N	2026-08-24 22:59:44.680752	\N
614	ST-01-0614	نجلاء خالد	خديجة	أنثى	يمني	مستمر	باقي	\N	2012-02-08	المنطقة	المدينة	صنعاء	\N	\N	\N	\N	1	11	32	18	\N	2026-08-24 22:59:44.680752	\N
615	ST-01-0615	هاشم رائد	رنا	ذكر	يمني	مستمر	محول	\N	2011-12-10	الحي	الشمالية	ذمار	\N	\N	\N	\N	1	11	32	50	\N	2026-08-24 22:59:44.680752	\N
616	ST-01-0616	يوسف إبراهيم	فاطمة	ذكر	يمني	مستمر	محول	\N	2017-12-04	الحي	المركز	المكلا	\N	\N	\N	\N	1	11	33	91	\N	2026-08-24 22:59:44.680752	\N
617	ST-01-0617	رحمة فهد	خديجة	أنثى	يمني	مستمر	باقي	\N	2012-10-07	المنطقة	المركز	المكلا	\N	\N	\N	\N	1	11	33	33	\N	2026-08-24 22:59:44.680752	\N
618	ST-01-0618	بدر حمد	هدى	ذكر	يمني	مستمر	محول	\N	2005-03-09	الشارع	المدينة	عدن	\N	\N	\N	\N	1	11	33	21	\N	2026-08-24 22:59:44.680752	\N
619	ST-01-0619	فهد سعود	صفاء	ذكر	يمني	انسحاب	باقي	\N	2015-08-03	القرية	المدينة	المكلا	\N	\N	\N	\N	1	11	33	92	\N	2026-08-24 22:59:44.680752	\N
620	ST-01-0620	تميم خالد	غادة	ذكر	يمني	مستمر	باقي	\N	2017-02-04	الحارة	المدينة	عدن	\N	\N	\N	\N	1	11	33	14	\N	2026-08-24 22:59:44.680752	\N
621	ST-01-0621	أنس محمد	جنات	ذكر	يمني	انسحاب	محول	\N	2006-07-26	الحارة	الجنوبية	المكلا	\N	\N	\N	\N	1	11	33	3	\N	2026-08-24 22:59:44.680752	\N
622	ST-01-0622	أكرم وجيه	ضحى	ذكر	يمني	مستمر	باقي	\N	2008-06-25	القرية	الشرقية	صنعاء	\N	\N	\N	\N	1	11	33	60	\N	2026-08-24 22:59:44.680752	\N
623	ST-01-0623	فارس خالد	رحمة	ذكر	يمني	مستمر	مستجد	\N	2009-05-23	الشارع	الجنوبية	إب	\N	\N	\N	\N	1	11	33	55	\N	2026-08-24 22:59:44.680752	\N
624	ST-01-0624	رنا يوسف	زينب	أنثى	يمني	انسحاب	مستجد	\N	2014-02-02	الحي	المركز	صنعاء	\N	\N	\N	\N	1	11	33	19	\N	2026-08-24 22:59:44.680752	\N
625	ST-01-0625	فرح خالد	زينب	أنثى	يمني	مستمر	باقي	\N	2006-07-07	المنطقة	المركز	الحديدة	\N	\N	\N	\N	1	11	33	18	\N	2026-08-24 22:59:44.680752	\N
626	ST-01-0626	مريم أحمد	غادة	أنثى	يمني	انسحاب	محول	\N	2010-10-13	الشارع	الجنوبية	عدن	\N	\N	\N	\N	1	11	33	31	\N	2026-08-24 22:59:44.680752	\N
627	ST-01-0627	ياسمين إبراهيم	أمل	أنثى	يمني	مستمر	محول	\N	2008-05-22	الشارع	الشمالية	عدن	\N	\N	\N	\N	1	11	33	54	\N	2026-08-24 22:59:44.680752	\N
628	ST-01-0628	شهد زياد	هدى	أنثى	يمني	مستمر	باقي	\N	2010-11-26	القرية	المركز	الحديدة	\N	\N	\N	\N	1	11	33	77	\N	2026-08-24 22:59:44.680752	\N
629	ST-01-0629	قيس مالك	فاطمة	ذكر	يمني	مستمر	محول	\N	2013-06-09	الحارة	المدينة	صنعاء	\N	\N	\N	\N	1	11	33	24	\N	2026-08-24 22:59:44.680752	\N
630	ST-01-0630	أمل ناصر	زينب	أنثى	يمني	مستمر	باقي	\N	2005-10-08	الحي	المدينة	صنعاء	\N	\N	\N	\N	1	11	33	82	\N	2026-08-24 22:59:44.680752	\N
631	ST-01-0631	لينا إبراهيم	غادة	أنثى	يمني	انسحاب	محول	\N	2011-04-14	الحي	الجنوبية	صنعاء	\N	\N	\N	\N	1	11	33	31	\N	2026-08-24 22:59:44.680752	\N
632	ST-01-0632	حمزة علي	فرح	ذكر	يمني	انسحاب	محول	\N	2010-02-10	الحارة	الغربية	حضرموت	\N	\N	\N	\N	1	11	33	72	\N	2026-08-24 22:59:44.680752	\N
651	ST-01-0651	محمود سامي	تقى	ذكر	يمني	مستمر	باقي	\N	2006-01-26	الحارة	الجنوبية	عدن	\N	\N	\N	\N	1	12	\N	97	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
693	1234123	ااحمد محمد احمد سعيد راوح	بب	ذكر	يمني	مستمر	مستجد	\N	2026-08-01	حرقه	مجمعه	تعز	\N	\N	\N	\N	1	1	1	16	\N	2026-08-24 23:54:28.69637	2026-09-01 04:09:51.404715
76	ST-01-0076	أكرم وجيه	مريم	ذكر	يمني	مستمر	باقي	\N	2014-07-16	القرية	المركز	حضرموت	\N	\N	\N	\N	1	2	3	65	\N	2026-08-24 22:59:44.680752	2026-08-25 03:39:46.169292
82	ST-01-0082	أكرم وجيه	شهد	ذكر	يمني	مستمر	باقي	\N	2017-05-15	الحارة	المركز	صنعاء	\N	\N	\N	\N	1	2	3	71	\N	2026-08-24 22:59:44.680752	2026-08-25 03:39:46.169292
537	ST-01-0537	أمل ناصر	قمر	أنثى	يمني	مستمر	باقي	\N	2011-07-20	الشارع	الجنوبية	تعز	\N	\N	\N	\N	1	10	3	5	\N	2026-08-24 22:59:44.680752	2026-08-25 03:40:50.606361
587	ST-01-0587	أحمد محمد	جنات	ذكر	يمني	مستمر	باقي	\N	2013-11-26	الشارع	الشمالية	حضرموت	\N	\N	\N	\N	1	11	31	35	\N	2026-08-24 22:59:44.680752	2026-08-27 01:01:22.769497
18	ST-01-0018	إبراهيم خليل	رنا	ذكر	يمني	مستمر	باقي	\N	2005-08-05	الشارع	المركز	تعز	\N	\N	\N	\N	1	1	1	4	\N	2026-08-24 22:59:44.680752	2026-08-30 02:51:38.281998
210	ST-01-0210	أنس محمد	نورة	ذكر	يمني	مستمر	باقي	\N	2011-04-05	القرية	الغربية	الحديدة	\N	\N	\N	\N	1	4	3	78	\N	2026-08-24 22:59:44.680752	2026-08-30 02:55:11.230283
523	ST-01-0523	وائل سامي	جنات	ذكر	يمني	مستمر	مستجد	\N	2017-09-16	القرية	الجنوبية	ذمار	\N	\N	\N	\N	1	10	\N	12	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
524	ST-01-0524	جنات محمد	جنات	أنثى	يمني	مستمر	باقي	\N	2012-03-21	القرية	المركز	تعز	\N	\N	\N	\N	1	10	\N	87	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
525	ST-01-0525	فهد سعود	فاطمة	ذكر	يمني	مستمر	باقي	\N	2014-07-23	المنطقة	الشمالية	إب	\N	\N	\N	\N	1	10	\N	59	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
526	ST-01-0526	نضال فؤاد	رحمة	ذكر	يمني	مستمر	باقي	\N	2010-02-11	القرية	الشرقية	ذمار	\N	\N	\N	\N	1	10	\N	4	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
527	ST-01-0527	تميم خالد	ضحى	ذكر	يمني	مستمر	باقي	\N	2007-10-11	المنطقة	الشرقية	ذمار	\N	\N	\N	\N	1	10	\N	34	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
528	ST-01-0528	حمزة علي	شهد	ذكر	يمني	مستمر	محول	\N	2006-05-03	المنطقة	المدينة	عدن	\N	\N	\N	\N	1	10	\N	7	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
529	ST-01-0529	لينا إبراهيم	سلمى	أنثى	يمني	مستمر	محول	\N	2012-08-20	الحي	الشرقية	عدن	\N	\N	\N	\N	1	10	\N	6	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
530	ST-01-0530	دينا حمد	لينا	أنثى	يمني	انسحاب	محول	\N	2012-09-17	الحي	المركز	الحديدة	\N	\N	\N	\N	1	10	\N	29	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
531	ST-01-0531	لينا إبراهيم	صفاء	أنثى	يمني	مستمر	محول	\N	2012-03-27	المنطقة	المدينة	صنعاء	\N	\N	\N	\N	1	10	\N	9	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
532	ST-01-0532	عمر خالد	صفاء	ذكر	يمني	مستمر	باقي	\N	2009-04-13	الحارة	الشرقية	تعز	\N	\N	\N	\N	1	10	\N	29	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
533	ST-01-0533	صفاء هشام	رنا	أنثى	يمني	مستمر	محول	\N	2016-05-03	الحي	الجنوبية	تعز	\N	\N	\N	\N	1	10	\N	13	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
534	ST-01-0534	مازن هاني	شهد	ذكر	يمني	انسحاب	باقي	\N	2005-05-13	القرية	الغربية	الحديدة	\N	\N	\N	\N	1	10	\N	88	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
535	ST-01-0535	زياد هشام	رحمة	ذكر	يمني	مستمر	محول	\N	2011-08-11	المنطقة	المدينة	صنعاء	\N	\N	\N	\N	1	10	\N	2	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
536	ST-01-0536	سارة خالد	خديجة	أنثى	يمني	مستمر	باقي	\N	2015-08-18	المنطقة	المدينة	الحديدة	\N	\N	\N	\N	1	10	\N	22	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
538	ST-01-0538	مودة عمر	غادة	أنثى	يمني	مستمر	مستجد	\N	2008-12-24	القرية	الغربية	عدن	\N	\N	\N	\N	1	10	\N	13	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
539	ST-01-0539	عمر خالد	رنا	ذكر	يمني	مستمر	محول	\N	2015-11-22	الحارة	الشرقية	إب	\N	\N	\N	\N	1	10	\N	66	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
540	ST-01-0540	سعيد علي	أمل	ذكر	يمني	مستمر	باقي	\N	2005-04-15	الحارة	الشرقية	المكلا	\N	\N	\N	\N	1	10	\N	45	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
541	ST-01-0541	فهد سعود	لينا	ذكر	يمني	مستمر	محول	\N	2018-06-23	الشارع	الشمالية	عدن	\N	\N	\N	\N	1	10	\N	75	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
542	ST-01-0542	محمد أحمد	دينا	ذكر	يمني	مستمر	باقي	\N	2005-05-10	الحي	الشمالية	الحديدة	\N	\N	\N	\N	1	10	\N	3	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
543	ST-01-0543	لمى حسن	سلمى	أنثى	يمني	انسحاب	باقي	\N	2005-09-14	الشارع	الشرقية	الحديدة	\N	\N	\N	\N	1	10	\N	12	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
544	ST-01-0544	ناصر عبدالعزيز	هدى	ذكر	يمني	مستمر	باقي	\N	2009-01-23	الشارع	الجنوبية	حضرموت	\N	\N	\N	\N	1	10	\N	12	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
545	ST-01-0545	مريم أحمد	نورة	أنثى	يمني	انسحاب	محول	\N	2012-09-22	القرية	المركز	عدن	\N	\N	\N	\N	1	10	\N	85	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
546	ST-01-0546	محمود سامي	غادة	ذكر	يمني	مستمر	محول	\N	2016-07-13	المنطقة	الغربية	إب	\N	\N	\N	\N	1	10	\N	14	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
547	ST-01-0547	حسن يوسف	قمر	ذكر	يمني	انسحاب	باقي	\N	2012-03-26	الحي	الشرقية	ذمار	\N	\N	\N	\N	1	10	\N	63	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
548	ST-01-0548	تقى سعود	شهد	أنثى	يمني	مستمر	باقي	\N	2014-09-11	الحارة	الشمالية	إب	\N	\N	\N	\N	1	10	\N	80	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
549	ST-01-0549	عائشة محمد	نورة	أنثى	يمني	مستمر	باقي	\N	2014-09-09	المنطقة	الشمالية	ذمار	\N	\N	\N	\N	1	10	\N	13	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
550	ST-01-0550	ناصر عبدالعزيز	شهد	ذكر	يمني	انسحاب	مستجد	\N	2013-02-02	المنطقة	الشمالية	ذمار	\N	\N	\N	\N	1	10	\N	96	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
551	ST-01-0551	وسن يوسف	شهد	أنثى	يمني	مستمر	باقي	\N	2012-08-14	الحي	المدينة	المكلا	\N	\N	\N	\N	1	10	\N	85	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
552	ST-01-0552	نورة عبدالله	سارة	أنثى	يمني	مستمر	محول	\N	2017-09-08	القرية	الغربية	حضرموت	\N	\N	\N	\N	1	10	\N	23	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
553	ST-01-0553	راشد علي	رحمة	ذكر	يمني	مستمر	باقي	\N	2017-01-17	الشارع	المركز	تعز	\N	\N	\N	\N	1	10	\N	97	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
554	ST-01-0554	سعيد علي	مريم	ذكر	يمني	مستمر	باقي	\N	2006-02-08	الحي	الشرقية	إب	\N	\N	\N	\N	1	10	\N	65	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
555	ST-01-0555	مريم أحمد	سارة	أنثى	يمني	انسحاب	مستجد	\N	2013-03-03	الحارة	المركز	الحديدة	\N	\N	\N	\N	1	10	\N	37	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
556	ST-01-0556	هبة عبدالله	مريم	أنثى	يمني	مستمر	باقي	\N	2007-06-15	المنطقة	الشمالية	حضرموت	\N	\N	\N	\N	1	10	\N	64	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
557	ST-01-0557	ياسمين إبراهيم	رحمة	أنثى	يمني	مستمر	محول	\N	2010-11-02	المنطقة	المدينة	تعز	\N	\N	\N	\N	1	10	\N	17	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
558	ST-01-0558	سلطان محمد	حنان	ذكر	يمني	مستمر	محول	\N	2005-12-23	الشارع	الشمالية	عدن	\N	\N	\N	\N	1	10	\N	49	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
559	ST-01-0559	لمى حسن	تقى	أنثى	يمني	مستمر	باقي	\N	2015-08-13	القرية	المدينة	إب	\N	\N	\N	\N	1	10	\N	65	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
560	ST-01-0560	أنس محمد	فرح	ذكر	يمني	مستمر	مستجد	\N	2013-01-15	الحارة	الغربية	حضرموت	\N	\N	\N	\N	1	10	\N	8	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
561	ST-01-0561	شهد زياد	زينب	أنثى	يمني	مستمر	مستجد	\N	2013-12-26	المنطقة	الجنوبية	الحديدة	\N	\N	\N	\N	1	10	\N	88	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
562	ST-01-0562	دينا حمد	رنا	أنثى	يمني	مستمر	باقي	\N	2005-11-22	القرية	الغربية	ذمار	\N	\N	\N	\N	1	10	\N	52	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
563	ST-01-0563	تقى سعود	مريم	أنثى	يمني	مستمر	باقي	\N	2011-06-21	الحارة	الشمالية	تعز	\N	\N	\N	\N	1	10	\N	62	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
564	ST-01-0564	زينب حسن	قمر	أنثى	يمني	مستمر	مستجد	\N	2006-12-04	الحارة	المدينة	الحديدة	\N	\N	\N	\N	1	10	\N	33	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
566	ST-01-0566	علي حسن	جنات	ذكر	يمني	مستمر	باقي	\N	2006-03-03	الحي	الجنوبية	ذمار	\N	\N	\N	\N	1	10	\N	54	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
567	ST-01-0567	زياد هشام	نورة	ذكر	يمني	مستمر	محول	\N	2013-05-22	المنطقة	الجنوبية	الحديدة	\N	\N	\N	\N	1	10	\N	100	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
568	ST-01-0568	عبدالله عمر	قمر	ذكر	يمني	مستمر	مستجد	\N	2011-10-17	الشارع	الجنوبية	عدن	\N	\N	\N	\N	1	10	\N	81	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
569	ST-01-0569	سعيد علي	تقى	ذكر	يمني	انسحاب	باقي	\N	2011-05-24	المنطقة	المدينة	تعز	\N	\N	\N	\N	1	10	\N	56	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
570	ST-01-0570	سعيد علي	سلمى	ذكر	يمني	مستمر	محول	\N	2007-10-05	الحارة	الجنوبية	تعز	\N	\N	\N	\N	1	10	\N	98	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
571	ST-01-0571	راشد علي	شهد	ذكر	يمني	مستمر	باقي	\N	2013-02-01	الشارع	الشمالية	صنعاء	\N	\N	\N	\N	1	10	\N	63	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
572	ST-01-0572	داود سليمان	عائشة	ذكر	يمني	مستمر	باقي	\N	2007-02-04	الحارة	الجنوبية	الحديدة	\N	\N	\N	\N	1	10	\N	72	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
573	ST-01-0573	هدى سامي	جنات	أنثى	يمني	انسحاب	باقي	\N	2017-07-11	المنطقة	الجنوبية	عدن	\N	\N	\N	\N	1	10	\N	46	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
574	ST-01-0574	وسن يوسف	صفاء	أنثى	يمني	مستمر	باقي	\N	2018-01-18	القرية	المدينة	صنعاء	\N	\N	\N	\N	1	10	\N	63	\N	2026-08-24 22:59:44.680752	2026-08-30 13:28:35.363585
633	ST-01-0633	زكريا يحيى	سارة	ذكر	يمني	مستمر	باقي	\N	2005-11-20	القرية	الغربية	تعز	\N	\N	\N	\N	1	12	\N	100	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
634	ST-01-0634	هبة عبدالله	فاطمة	أنثى	يمني	انسحاب	باقي	\N	2016-01-23	الحارة	الشمالية	المكلا	\N	\N	\N	\N	1	12	\N	47	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
635	ST-01-0635	بسمة فهد	جنات	أنثى	يمني	مستمر	باقي	\N	2013-09-06	الحارة	الشمالية	المكلا	\N	\N	\N	\N	1	12	\N	85	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
636	ST-01-0636	رحمة فهد	غادة	أنثى	يمني	مستمر	محول	\N	2018-10-24	الحي	المركز	إب	\N	\N	\N	\N	1	12	\N	91	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
637	ST-01-0637	كرم نبيل	مريم	ذكر	يمني	مستمر	مستجد	\N	2009-08-18	الحارة	الجنوبية	المكلا	\N	\N	\N	\N	1	12	\N	26	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
638	ST-01-0638	أكرم وجيه	حنان	ذكر	يمني	مستمر	مستجد	\N	2016-04-21	القرية	الشرقية	الحديدة	\N	\N	\N	\N	1	12	\N	47	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
639	ST-01-0639	لمى حسن	ضحى	أنثى	يمني	مستمر	باقي	\N	2014-02-14	المنطقة	الجنوبية	صنعاء	\N	\N	\N	\N	1	12	\N	76	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
640	ST-01-0640	أمل ناصر	بسمة	أنثى	يمني	مستمر	باقي	\N	2005-12-02	الشارع	الشمالية	الحديدة	\N	\N	\N	\N	1	12	\N	96	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
641	ST-01-0641	حسن يوسف	حنان	ذكر	يمني	مستمر	محول	\N	2008-09-20	الحارة	الغربية	المكلا	\N	\N	\N	\N	1	12	\N	32	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
642	ST-01-0642	أنس محمد	نورة	ذكر	يمني	مستمر	باقي	\N	2011-12-19	المنطقة	المدينة	ذمار	\N	\N	\N	\N	1	12	\N	64	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
643	ST-01-0643	فاطمة علي	سلمى	أنثى	يمني	مستمر	باقي	\N	2009-08-26	القرية	الشرقية	ذمار	\N	\N	\N	\N	1	12	\N	76	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
644	ST-01-0644	ماجد فهد	رحمة	ذكر	يمني	مستمر	باقي	\N	2014-05-24	القرية	الجنوبية	صنعاء	\N	\N	\N	\N	1	12	\N	55	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
645	ST-01-0645	هدى سامي	سارة	أنثى	يمني	مستمر	محول	\N	2014-06-19	المنطقة	المدينة	إب	\N	\N	\N	\N	1	12	\N	88	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
646	ST-01-0646	رنا يوسف	نورة	أنثى	يمني	مستمر	محول	\N	2006-05-01	الحي	الغربية	إب	\N	\N	\N	\N	1	12	\N	20	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
647	ST-01-0647	محمد أحمد	سارة	ذكر	يمني	مستمر	باقي	\N	2018-11-07	الشارع	المركز	الحديدة	\N	\N	\N	\N	1	12	\N	10	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
648	ST-01-0648	بلال أحمد	قمر	ذكر	يمني	مستمر	محول	\N	2013-07-10	الحي	المركز	تعز	\N	\N	\N	\N	1	12	\N	67	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
649	ST-01-0649	أكرم وجيه	بسمة	ذكر	يمني	مستمر	مستجد	\N	2014-09-06	القرية	المدينة	صنعاء	\N	\N	\N	\N	1	12	\N	23	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
650	ST-01-0650	هدى سامي	زينب	أنثى	يمني	مستمر	باقي	\N	2009-07-28	الحارة	الشمالية	ذمار	\N	\N	\N	\N	1	12	\N	82	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
652	ST-01-0652	عاصم عمر	تقى	ذكر	يمني	مستمر	محول	\N	2010-06-23	الحي	المدينة	المكلا	\N	\N	\N	\N	1	12	\N	63	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
653	ST-01-0653	رنا يوسف	أمل	أنثى	يمني	مستمر	باقي	\N	2012-05-25	الحي	الغربية	صنعاء	\N	\N	\N	\N	1	12	\N	27	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
654	ST-01-0654	قمر علي	صفاء	أنثى	يمني	مستمر	باقي	\N	2014-08-15	الحي	الغربية	الحديدة	\N	\N	\N	\N	1	12	\N	48	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
655	ST-01-0655	سعيد علي	بسمة	ذكر	يمني	مستمر	محول	\N	2018-07-12	القرية	الجنوبية	حضرموت	\N	\N	\N	\N	1	12	\N	5	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
656	ST-01-0656	عمر خالد	لينا	ذكر	يمني	مستمر	مستجد	\N	2012-06-10	الشارع	المركز	إب	\N	\N	\N	\N	1	12	\N	34	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
657	ST-01-0657	فهد سعود	غادة	ذكر	يمني	انسحاب	باقي	\N	2012-01-19	الشارع	الشمالية	ذمار	\N	\N	\N	\N	1	12	\N	52	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
658	ST-01-0658	وائل سامي	بسمة	ذكر	يمني	انسحاب	باقي	\N	2009-05-27	الحارة	المدينة	المكلا	\N	\N	\N	\N	1	12	\N	50	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
659	ST-01-0659	نجلاء خالد	حنان	أنثى	يمني	انسحاب	مستجد	\N	2014-07-08	المنطقة	الشمالية	حضرموت	\N	\N	\N	\N	1	12	\N	78	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
660	ST-01-0660	شهد زياد	رنا	أنثى	يمني	مستمر	مستجد	\N	2018-02-01	الحارة	المركز	صنعاء	\N	\N	\N	\N	1	12	\N	8	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
661	ST-01-0661	عمر خالد	مريم	ذكر	يمني	مستمر	باقي	\N	2015-12-14	الشارع	الجنوبية	تعز	\N	\N	\N	\N	1	12	\N	39	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
662	ST-01-0662	أمل ناصر	دينا	أنثى	يمني	انسحاب	باقي	\N	2007-05-09	الحارة	المدينة	المكلا	\N	\N	\N	\N	1	12	\N	44	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
663	ST-01-0663	وليد طلال	مريم	ذكر	يمني	مستمر	باقي	\N	2007-09-15	الحي	الشمالية	إب	\N	\N	\N	\N	1	12	\N	16	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
664	ST-01-0664	سلمى طلال	شهد	أنثى	يمني	مستمر	باقي	\N	2012-08-23	القرية	الجنوبية	الحديدة	\N	\N	\N	\N	1	12	\N	24	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
665	ST-01-0665	سعيد علي	سلمى	ذكر	يمني	انسحاب	باقي	\N	2006-02-22	المنطقة	الشمالية	إب	\N	\N	\N	\N	1	12	\N	35	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
667	ST-01-0667	نضال فؤاد	دينا	ذكر	يمني	انسحاب	باقي	\N	2011-02-18	الشارع	المدينة	الحديدة	\N	\N	\N	\N	1	12	\N	43	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
668	ST-01-0668	نجلاء خالد	ضحى	أنثى	يمني	مستمر	مستجد	\N	2009-09-01	الحارة	المدينة	حضرموت	\N	\N	\N	\N	1	12	\N	84	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
669	ST-01-0669	وليد طلال	دينا	ذكر	يمني	مستمر	مستجد	\N	2017-11-14	الشارع	الجنوبية	صنعاء	\N	\N	\N	\N	1	12	\N	60	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
670	ST-01-0670	تقى سعود	عائشة	أنثى	يمني	مستمر	مستجد	\N	2013-03-24	القرية	المركز	المكلا	\N	\N	\N	\N	1	12	\N	20	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
671	ST-01-0671	تقى سعود	شهد	أنثى	يمني	مستمر	مستجد	\N	2014-05-03	الحي	المدينة	حضرموت	\N	\N	\N	\N	1	12	\N	23	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
672	ST-01-0672	خديجة عمر	ضحى	أنثى	يمني	مستمر	باقي	\N	2014-02-17	الشارع	الشرقية	إب	\N	\N	\N	\N	1	12	\N	30	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
673	ST-01-0673	سعيد علي	زينب	ذكر	يمني	انسحاب	محول	\N	2011-12-14	الشارع	المركز	عدن	\N	\N	\N	\N	1	12	\N	52	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
674	ST-01-0674	قمر علي	بسمة	أنثى	يمني	مستمر	باقي	\N	2015-03-28	المنطقة	المركز	حضرموت	\N	\N	\N	\N	1	12	\N	19	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
675	ST-01-0675	وائل سامي	غادة	ذكر	يمني	مستمر	مستجد	\N	2009-05-20	المنطقة	الشرقية	إب	\N	\N	\N	\N	1	12	\N	87	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
676	ST-01-0676	فهد سعود	زينب	ذكر	يمني	مستمر	باقي	\N	2008-11-23	الحارة	الغربية	ذمار	\N	\N	\N	\N	1	12	\N	9	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
677	ST-01-0677	صفاء هشام	ضحى	أنثى	يمني	مستمر	محول	\N	2015-04-14	القرية	المركز	الحديدة	\N	\N	\N	\N	1	12	\N	72	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
678	ST-01-0678	وليد طلال	هدى	ذكر	يمني	انسحاب	باقي	\N	2011-05-28	الشارع	الشمالية	ذمار	\N	\N	\N	\N	1	12	\N	99	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
679	ST-01-0679	تقى سعود	فاطمة	أنثى	يمني	مستمر	محول	\N	2017-11-10	المنطقة	الغربية	تعز	\N	\N	\N	\N	1	12	\N	56	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
680	ST-01-0680	وليد طلال	تقى	ذكر	يمني	مستمر	باقي	\N	2008-09-09	الشارع	الشمالية	المكلا	\N	\N	\N	\N	1	12	\N	32	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
681	ST-01-0681	صفاء هشام	تقى	أنثى	يمني	مستمر	مستجد	\N	2014-11-28	الحارة	المدينة	المكلا	\N	\N	\N	\N	1	12	\N	77	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
683	ST-01-0683	سارة خالد	بسمة	أنثى	يمني	مستمر	باقي	\N	2015-10-02	القرية	الشرقية	صنعاء	\N	\N	\N	\N	1	12	\N	13	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
684	ST-01-0684	محمد أحمد	زينب	ذكر	يمني	مستمر	باقي	\N	2009-11-01	الحارة	المدينة	ذمار	\N	\N	\N	\N	1	12	\N	40	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
685	ST-01-0685	قمر علي	أمل	أنثى	يمني	مستمر	محول	\N	2009-07-23	المنطقة	الشمالية	صنعاء	\N	\N	\N	\N	1	12	\N	95	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
686	ST-01-0686	نجلاء خالد	فاطمة	أنثى	يمني	مستمر	باقي	\N	2014-02-06	الشارع	الجنوبية	صنعاء	\N	\N	\N	\N	1	12	\N	26	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
687	ST-01-0687	هبة عبدالله	جنات	أنثى	يمني	انسحاب	محول	\N	2013-10-21	المنطقة	الجنوبية	عدن	\N	\N	\N	\N	1	12	\N	80	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
688	ST-01-0688	طارق زياد	فاطمة	ذكر	يمني	انسحاب	باقي	\N	2010-10-21	الحارة	المركز	حضرموت	\N	\N	\N	\N	1	12	\N	63	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
689	ST-01-0689	هاشم رائد	حنان	ذكر	يمني	مستمر	محول	\N	2007-10-18	المنطقة	الغربية	المكلا	\N	\N	\N	\N	1	12	\N	1	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
690	ST-01-0690	نجلاء خالد	رحمة	أنثى	يمني	مستمر	باقي	\N	2010-12-18	الحي	المركز	إب	\N	\N	\N	\N	1	12	\N	71	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
691	ST-01-0691	خالد عبدالله	هدى	ذكر	يمني	مستمر	باقي	\N	2009-12-05	القرية	المركز	المكلا	\N	\N	\N	\N	1	12	\N	39	\N	2026-08-24 22:59:44.680752	2026-08-30 13:41:48.074101
692	123456	خالد محمد احمد سعيد راوح	حوى	ذكر	يمني	مستمر	مستجد	\N	2026-08-24	\N	\N	\N	\N	\N	\N	\N	1	12	\N	\N	\N	2026-08-24 23:34:52.607418	2026-08-30 13:41:48.074101
682	ST-01-0682	آدم نوح	شهد	ذكر	يمني	مستمر	محول	\N	2007-03-28	القرية	المركز	تعز	\N	\N	\N	\N	1	12	68	67	\N	2026-08-24 22:59:44.680752	2026-09-01 04:01:32.523337
\.


--
-- Data for Name: subjects; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.subjects (id, subject_name, min_pass_score, max_score, created_at, updated_at) FROM stdin;
1	القرآن الكريم	50.00	100.00	2026-08-21 02:18:55.761119	\N
2	التربية الإسلامية	50.00	100.00	2026-08-21 02:18:55.761119	\N
3	اللغة العربية	50.00	100.00	2026-08-21 02:18:55.761119	\N
4	اللغة الإنجليزية	50.00	100.00	2026-08-21 02:18:55.761119	\N
5	الرياضيات	50.00	100.00	2026-08-21 02:18:55.761119	\N
6	العلوم	50.00	100.00	2026-08-21 02:18:55.761119	\N
7	الدراسات الاجتماعية	50.00	100.00	2026-08-21 02:18:55.761119	\N
8	الحاسوب	50.00	100.00	2026-08-21 02:18:55.761119	\N
9	التربية الفنية	50.00	100.00	2026-08-21 02:18:55.761119	\N
10	التربية البدنية	50.00	100.00	2026-08-21 02:18:55.761119	\N
\.


--
-- Data for Name: system_audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_audit_logs (id, user_id, module_name, operation_type, record_id, old_values, new_values, ip_address, device_name, created_at, updated_at) FROM stdin;
36	2	تسجيل الدخول	login	\N	\N	\N	10.12.42.92	عبود	2026-08-30 18:20:32.350655	\N
37	2	تسجيل الخروج	logout	\N	\N	\N	10.12.42.92	عبود	2026-08-30 18:22:03.505565	\N
38	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 03:25:20.125388	\N
25	2	تسجيل الدخول	login	\N	\N	\N	10.12.42.92	عبود	2026-08-30 18:09:25.8799	\N
26	2	الطلاب	delete	134	{"student_number": "ST-01-0134", "full_name": "آدم نوح"}	\N	10.12.42.92	عبود	2026-08-30 18:09:40.633261	\N
27	2	students	delete	134	{"id": "134", "student_number": "ST-01-0134", "full_name": "آدم نوح", "mother_name": "مريم", "gender": "ذكر", "nationality": "يمني", "status": "انسحاب", "enrollment_type": "مستجد", "student_status_reason": "None", "birth_date": "2007-08-20", "birth_village": "الشارع", "birth_district": "الغربية", "birth_governorate": "تعز", "transferred_from_school": "None", "transferred_district": "None", "transferred_governorate": "None", "transfer_date": "None", "academic_year_id": "1", "grade_id": "3", "section_id": "8", "parent_id": "9", "photo_url": "None", "created_at": "2026-08-24 22:59:44.680752", "updated_at": "None"}	\N	10.12.42.92	عبود	2026-08-30 18:09:40.633261	\N
28	2	students	create	695	\N	{"id": "695", "student_number": "w", "full_name": "ww", "mother_name": "None", "gender": "ذكر", "nationality": "يمني", "status": "مستمر", "enrollment_type": "مستجد", "student_status_reason": "None", "birth_date": "2026-08-30", "birth_village": "None", "birth_district": "None", "birth_governorate": "None", "transferred_from_school": "None", "transferred_district": "None", "transferred_governorate": "None", "transfer_date": "None", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "parent_id": "None", "photo_url": "None", "created_at": "2026-08-30 18:12:59.905236", "updated_at": "None"}	10.12.42.92	عبود	2026-08-30 18:12:59.905236	\N
29	2	الطلاب	create	\N	\N	{"action": "إضافة طالب جديد"}	10.12.42.92	عبود	2026-08-30 18:12:59.924223	\N
30	2	تسجيل الخروج	logout	\N	\N	\N	10.12.42.92	عبود	2026-08-30 18:15:49.436129	\N
31	2	تسجيل الدخول	login	\N	\N	\N	10.12.42.92	عبود	2026-08-30 18:15:57.535258	\N
32	2	الطلاب	delete	695	{"student_number": "w", "full_name": "ww"}	\N	10.12.42.92	عبود	2026-08-30 18:16:25.20837	\N
33	2	الطلاب	delete	695	"{Ellipsis}"	\N	10.12.42.92	عبود	2026-08-30 18:16:25.20837	\N
34	2	students	delete	695	{"id": "695", "student_number": "w", "full_name": "ww", "mother_name": "None", "gender": "ذكر", "nationality": "يمني", "status": "مستمر", "enrollment_type": "مستجد", "student_status_reason": "None", "birth_date": "2026-08-30", "birth_village": "None", "birth_district": "None", "birth_governorate": "None", "transferred_from_school": "None", "transferred_district": "None", "transferred_governorate": "None", "transfer_date": "None", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "parent_id": "None", "photo_url": "None", "created_at": "2026-08-30 18:12:59.905236", "updated_at": "None"}	\N	10.12.42.92	عبود	2026-08-30 18:16:25.20837	\N
35	2	تسجيل الدخول	login	\N	\N	\N	10.12.42.92	عبود	2026-08-30 18:16:54.211985	\N
39	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 03:33:35.633563	\N
40	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 03:35:49.458801	\N
41	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 03:40:11.433169	\N
42	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 03:40:20.218597	\N
43	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 03:40:39.032811	\N
44	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 03:40:46.203686	\N
45	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 03:42:38.460803	\N
46	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 03:42:46.351814	\N
47	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 03:45:57.150907	\N
48	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 03:46:15.118092	\N
49	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 03:58:29.034359	\N
50	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 03:58:37.047582	\N
51	2	الطلاب	create	682	\N	"{Ellipsis}"	192.168.56.1	عبود	2026-09-01 04:01:32.523337	\N
52	2	الطلاب	create	358	\N	"{Ellipsis}"	192.168.56.1	عبود	2026-09-01 04:01:38.257259	\N
53	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 04:07:08.56138	\N
54	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 04:07:16.395883	\N
55	2	الطلاب	create	693	\N	"{Ellipsis}"	192.168.56.1	عبود	2026-09-01 04:08:54.919992	\N
56	2	fee_installments	delete	264	{"id": "264", "student_fee_id": "3", "installment_type": "regular", "installment_number": "1", "installment_name": "ww", "amount": "118825.67", "due_date": "2026-09-27", "is_paid": "False", "paid_amount": "0.00", "created_at": "2026-08-27 03:36:51.947244", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-01 04:16:22.615934	\N
57	2	fee_installments	delete	265	{"id": "265", "student_fee_id": "3", "installment_type": "regular", "installment_number": "2", "installment_name": "قسط 2", "amount": "118825.67", "due_date": "2026-10-27", "is_paid": "False", "paid_amount": "0.00", "created_at": "2026-08-27 03:36:51.947244", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-01 04:16:22.615934	\N
58	2	fee_installments	delete	266	{"id": "266", "student_fee_id": "3", "installment_type": "regular", "installment_number": "3", "installment_name": "قسط 3", "amount": "118825.67", "due_date": "2026-11-27", "is_paid": "False", "paid_amount": "0.00", "created_at": "2026-08-27 03:36:51.947244", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-01 04:16:22.615934	\N
59	2	fee_installments	create	267	\N	{"id": "267", "student_fee_id": "3", "installment_type": "regular", "installment_number": "1", "installment_name": "قسط 1", "amount": "6087.0", "due_date": "2026-10-01", "is_paid": "False", "paid_amount": "0.00", "created_at": "2026-09-01 04:16:22.615934", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 04:16:22.615934	\N
60	2	fee_installments	create	268	\N	{"id": "268", "student_fee_id": "3", "installment_type": "regular", "installment_number": "2", "installment_name": "قسط 2", "amount": "6087.0", "due_date": "2026-11-01", "is_paid": "False", "paid_amount": "0.00", "created_at": "2026-09-01 04:16:22.615934", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 04:16:22.615934	\N
61	2	fee_installments	create	269	\N	{"id": "269", "student_fee_id": "3", "installment_type": "regular", "installment_number": "3", "installment_name": "قسط 3", "amount": "6087.0", "due_date": "2026-12-01", "is_paid": "False", "paid_amount": "0.00", "created_at": "2026-09-01 04:16:22.615934", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 04:16:22.615934	\N
62	2	fee_installments	delete	267	{"id": "267", "student_fee_id": "3", "installment_type": "regular", "installment_number": "1", "installment_name": "قسط 1", "amount": "6087.00", "due_date": "2026-10-01", "is_paid": "False", "paid_amount": "0.00", "created_at": "2026-09-01 04:16:22.615934", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-01 04:17:07.919896	\N
63	2	fee_installments	delete	268	{"id": "268", "student_fee_id": "3", "installment_type": "regular", "installment_number": "2", "installment_name": "قسط 2", "amount": "6087.00", "due_date": "2026-11-01", "is_paid": "False", "paid_amount": "0.00", "created_at": "2026-09-01 04:16:22.615934", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-01 04:17:07.919896	\N
64	2	fee_installments	delete	269	{"id": "269", "student_fee_id": "3", "installment_type": "regular", "installment_number": "3", "installment_name": "قسط 3", "amount": "6087.00", "due_date": "2026-12-01", "is_paid": "False", "paid_amount": "0.00", "created_at": "2026-09-01 04:16:22.615934", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-01 04:17:07.919896	\N
65	2	fee_installments	create	270	\N	{"id": "270", "student_fee_id": "3", "installment_type": "regular", "installment_number": "1", "installment_name": "d", "amount": "6087.0", "due_date": "2026-10-01", "is_paid": "False", "paid_amount": "0.00", "created_at": "2026-09-01 04:17:07.919896", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 04:17:07.919896	\N
66	2	fee_installments	create	271	\N	{"id": "271", "student_fee_id": "3", "installment_type": "regular", "installment_number": "2", "installment_name": "قسط 2", "amount": "6087.0", "due_date": "2026-11-01", "is_paid": "False", "paid_amount": "0.00", "created_at": "2026-09-01 04:17:07.919896", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 04:17:07.919896	\N
67	2	fee_installments	create	272	\N	{"id": "272", "student_fee_id": "3", "installment_type": "regular", "installment_number": "3", "installment_name": "قسط 3", "amount": "6087.0", "due_date": "2026-12-01", "is_paid": "False", "paid_amount": "0.00", "created_at": "2026-09-01 04:17:07.919896", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 04:17:07.919896	\N
68	2	fee_installments	delete	7	{"id": "7", "student_fee_id": "4", "installment_type": "regular", "installment_number": "1", "installment_name": "قسط 1", "amount": "184188.00", "due_date": "2026-09-15", "is_paid": "True", "paid_amount": "184188.00", "created_at": "2026-08-24 22:59:44.680752", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-01 04:31:52.503296	\N
69	2	fee_installments	delete	8	{"id": "8", "student_fee_id": "4", "installment_type": "regular", "installment_number": "2", "installment_name": "قسط 2", "amount": "184188.00", "due_date": "2026-11-15", "is_paid": "True", "paid_amount": "184188.00", "created_at": "2026-08-24 22:59:44.680752", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-01 04:31:52.503296	\N
70	2	fee_installments	create	273	\N	{"id": "273", "student_fee_id": "4", "installment_type": "regular", "installment_number": "1", "installment_name": "قسط 1", "amount": "119258.0", "due_date": "2026-10-01", "is_paid": "False", "paid_amount": "0.00", "created_at": "2026-09-01 04:31:52.503296", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 04:31:52.503296	\N
71	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 04:34:24.52877	\N
72	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 04:34:32.390575	\N
438	2	تسجيل الخروج	logout	\N	\N	\N	10.13.84.80	عبود	2026-09-02 03:52:09.60983	\N
443	2	تسجيل الدخول	login	\N	\N	\N	10.13.84.80	عبود	2026-09-02 03:59:02.230871	\N
73	2	fee_installments	delete	273	{"id": "273", "student_fee_id": "4", "installment_type": "regular", "installment_number": "1", "installment_name": "قسط 1", "amount": "119258.00", "due_date": "2026-10-01", "is_paid": "False", "paid_amount": "0.00", "created_at": "2026-09-01 04:31:52.503296", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-01 04:35:22.991787	\N
74	2	fee_installments	create	274	\N	{"id": "274", "student_fee_id": "4", "installment_type": "regular", "installment_number": "1", "installment_name": "قسط 1", "amount": "30160.0", "due_date": "2026-10-01", "is_paid": "False", "paid_amount": "0.00", "created_at": "2026-09-01 04:35:22.991787", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 04:35:22.991787	\N
75	2	receipts	create	119	\N	{"id": "119", "receipt_number": "RCV-20260901043547", "student_id": "4", "installment_id": "274", "payment_target": "current_fee", "amount_paid": "20000.0", "payment_date": "2026-09-01 04:36:18.912967", "payment_method": "نقداً", "reference_number": "None", "notes": "None", "created_by_user_id": "2", "status": "نشط", "cancellation_reason": "None", "cancelled_at": "None", "created_at": "2026-09-01 04:36:18.912967", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 04:36:18.912967	\N
76	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 04:42:38.910627	\N
77	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 04:42:46.106363	\N
78	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 04:45:36.394164	\N
79	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 04:45:46.071174	\N
80	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 04:47:28.000408	\N
81	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 04:47:36.072344	\N
82	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 04:48:11.764369	\N
83	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 04:48:19.482211	\N
84	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 04:49:13.545927	\N
85	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 04:49:21.621658	\N
86	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 04:51:05.672683	\N
87	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 04:51:15.407049	\N
88	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 05:08:07.295275	\N
89	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 05:08:17.222617	\N
90	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 05:14:16.443342	\N
91	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 05:16:41.202066	\N
92	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 05:16:52.741546	\N
93	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 05:17:42.059774	\N
94	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 05:17:56.345874	\N
95	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 05:18:44.3838	\N
96	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 05:18:52.190244	\N
97	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 05:22:51.138424	\N
98	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 05:22:59.533085	\N
99	2	payroll_records	create	41	\N	{"id": "41", "employee_id": "1", "month": "9", "year": "2026", "basic_salary": "0.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "0.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
100	2	payroll_records	create	42	\N	{"id": "42", "employee_id": "10", "month": "9", "year": "2026", "basic_salary": "147433.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "147433.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
101	2	payroll_records	create	43	\N	{"id": "43", "employee_id": "5", "month": "9", "year": "2026", "basic_salary": "111926.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "16641.92", "net_salary": "95284.08", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
102	2	payroll_records	create	44	\N	{"id": "44", "employee_id": "6", "month": "9", "year": "2026", "basic_salary": "236904.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "45988.00", "net_salary": "190916.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
103	2	payroll_records	create	45	\N	{"id": "45", "employee_id": "8", "month": "9", "year": "2026", "basic_salary": "227081.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "227081.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
104	2	payroll_records	create	46	\N	{"id": "46", "employee_id": "11", "month": "9", "year": "2026", "basic_salary": "127427.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "31260.25", "net_salary": "96166.75", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
105	2	payroll_records	create	47	\N	{"id": "47", "employee_id": "12", "month": "9", "year": "2026", "basic_salary": "248985.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "21407.22", "net_salary": "227577.78", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
106	2	payroll_records	create	48	\N	{"id": "48", "employee_id": "13", "month": "9", "year": "2026", "basic_salary": "128636.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "128636.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
107	2	payroll_records	create	49	\N	{"id": "49", "employee_id": "14", "month": "9", "year": "2026", "basic_salary": "212050.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "16732.38", "net_salary": "195317.62", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
108	2	payroll_records	create	50	\N	{"id": "50", "employee_id": "15", "month": "9", "year": "2026", "basic_salary": "163636.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "163636.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
109	2	payroll_records	create	51	\N	{"id": "51", "employee_id": "16", "month": "9", "year": "2026", "basic_salary": "123808.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "123808.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
110	2	payroll_records	create	52	\N	{"id": "52", "employee_id": "18", "month": "9", "year": "2026", "basic_salary": "100303.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "100303.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
111	2	payroll_records	create	53	\N	{"id": "53", "employee_id": "19", "month": "9", "year": "2026", "basic_salary": "168836.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "168836.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
112	2	payroll_records	create	54	\N	{"id": "54", "employee_id": "20", "month": "9", "year": "2026", "basic_salary": "118026.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "118026.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
113	2	payroll_records	create	55	\N	{"id": "55", "employee_id": "22", "month": "9", "year": "2026", "basic_salary": "97649.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "97649.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
114	2	payroll_records	create	56	\N	{"id": "56", "employee_id": "23", "month": "9", "year": "2026", "basic_salary": "117980.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "117980.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
115	2	payroll_records	create	57	\N	{"id": "57", "employee_id": "24", "month": "9", "year": "2026", "basic_salary": "169821.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "169821.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
116	2	payroll_records	create	58	\N	{"id": "58", "employee_id": "25", "month": "9", "year": "2026", "basic_salary": "167367.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "167367.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
117	2	payroll_records	create	59	\N	{"id": "59", "employee_id": "27", "month": "9", "year": "2026", "basic_salary": "197153.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "197153.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
118	2	payroll_records	create	60	\N	{"id": "60", "employee_id": "28", "month": "9", "year": "2026", "basic_salary": "173838.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "173838.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
119	2	payroll_records	create	61	\N	{"id": "61", "employee_id": "29", "month": "9", "year": "2026", "basic_salary": "213489.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "213489.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
120	2	payroll_records	create	62	\N	{"id": "62", "employee_id": "30", "month": "9", "year": "2026", "basic_salary": "129386.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "129386.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
121	2	payroll_records	create	63	\N	{"id": "63", "employee_id": "31", "month": "9", "year": "2026", "basic_salary": "229136.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "229136.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
122	2	payroll_records	create	64	\N	{"id": "64", "employee_id": "34", "month": "9", "year": "2026", "basic_salary": "170565.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "170565.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
123	2	payroll_records	create	65	\N	{"id": "65", "employee_id": "32", "month": "9", "year": "2026", "basic_salary": "91759.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "91759.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:23:37.761486", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:23:37.761486	\N
124	2	payroll_records	create	66	\N	{"id": "66", "employee_id": "1", "month": "6", "year": "2026", "basic_salary": "0.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "0.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
125	2	payroll_records	create	67	\N	{"id": "67", "employee_id": "10", "month": "6", "year": "2026", "basic_salary": "147433.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "147433.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
126	2	payroll_records	create	68	\N	{"id": "68", "employee_id": "5", "month": "6", "year": "2026", "basic_salary": "111926.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "16641.92", "net_salary": "95284.08", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
127	2	payroll_records	create	69	\N	{"id": "69", "employee_id": "6", "month": "6", "year": "2026", "basic_salary": "236904.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "45988.00", "net_salary": "190916.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
128	2	payroll_records	create	70	\N	{"id": "70", "employee_id": "8", "month": "6", "year": "2026", "basic_salary": "227081.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "227081.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
129	2	payroll_records	create	71	\N	{"id": "71", "employee_id": "11", "month": "6", "year": "2026", "basic_salary": "127427.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "31260.25", "net_salary": "96166.75", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
130	2	payroll_records	create	72	\N	{"id": "72", "employee_id": "12", "month": "6", "year": "2026", "basic_salary": "248985.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "21407.22", "net_salary": "227577.78", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
131	2	payroll_records	create	73	\N	{"id": "73", "employee_id": "13", "month": "6", "year": "2026", "basic_salary": "128636.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "128636.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
132	2	payroll_records	create	74	\N	{"id": "74", "employee_id": "14", "month": "6", "year": "2026", "basic_salary": "212050.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "16732.38", "net_salary": "195317.62", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
133	2	payroll_records	create	75	\N	{"id": "75", "employee_id": "15", "month": "6", "year": "2026", "basic_salary": "163636.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "163636.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
134	2	payroll_records	create	76	\N	{"id": "76", "employee_id": "16", "month": "6", "year": "2026", "basic_salary": "123808.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "123808.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
135	2	payroll_records	create	77	\N	{"id": "77", "employee_id": "18", "month": "6", "year": "2026", "basic_salary": "100303.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "100303.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
136	2	payroll_records	create	78	\N	{"id": "78", "employee_id": "19", "month": "6", "year": "2026", "basic_salary": "168836.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "168836.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
137	2	payroll_records	create	79	\N	{"id": "79", "employee_id": "20", "month": "6", "year": "2026", "basic_salary": "118026.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "118026.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
138	2	payroll_records	create	80	\N	{"id": "80", "employee_id": "22", "month": "6", "year": "2026", "basic_salary": "97649.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "97649.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
139	2	payroll_records	create	81	\N	{"id": "81", "employee_id": "23", "month": "6", "year": "2026", "basic_salary": "117980.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "117980.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
140	2	payroll_records	create	82	\N	{"id": "82", "employee_id": "24", "month": "6", "year": "2026", "basic_salary": "169821.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "169821.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
141	2	payroll_records	create	83	\N	{"id": "83", "employee_id": "25", "month": "6", "year": "2026", "basic_salary": "167367.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "167367.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
142	2	payroll_records	create	84	\N	{"id": "84", "employee_id": "27", "month": "6", "year": "2026", "basic_salary": "197153.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "197153.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
143	2	payroll_records	create	85	\N	{"id": "85", "employee_id": "28", "month": "6", "year": "2026", "basic_salary": "173838.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "173838.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
144	2	payroll_records	create	86	\N	{"id": "86", "employee_id": "29", "month": "6", "year": "2026", "basic_salary": "213489.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "213489.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
145	2	payroll_records	create	87	\N	{"id": "87", "employee_id": "30", "month": "6", "year": "2026", "basic_salary": "129386.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "129386.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
146	2	payroll_records	create	88	\N	{"id": "88", "employee_id": "31", "month": "6", "year": "2026", "basic_salary": "229136.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "229136.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
147	2	payroll_records	create	89	\N	{"id": "89", "employee_id": "34", "month": "6", "year": "2026", "basic_salary": "170565.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "170565.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
148	2	payroll_records	create	90	\N	{"id": "90", "employee_id": "32", "month": "6", "year": "2026", "basic_salary": "91759.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "91759.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-01 05:24:03.566655", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:24:03.566655	\N
149	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 05:30:50.556162	\N
150	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 05:31:01.934736	\N
151	2	employee_loans	create	8	\N	{"id": "8", "employee_id": "5", "total_loan_amount": "20000.0", "monthly_deduction": "4.0", "status": "مستمرة", "loan_date": "2026-09-01", "reason": "None", "created_at": "2026-09-01 05:32:33.618972", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 05:32:33.618972	\N
152	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:05:57.87018	\N
153	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:06:05.932736	\N
154	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:08:38.025666	\N
155	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:09:13.71614	\N
156	2	monthly_evaluations	create	618	\N	{"id": "618", "student_id": "693", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "subject_id": "2", "term": "1", "month": "1", "written_score": "40.0", "oral_score": "20.0", "homework_score": "20.0", "attendance_score": "20.0", "created_at": "2026-09-01 06:12:38.315532", "updated_at": "None"}	192.168.56.1	عبود	2026-09-01 06:12:38.315532	\N
157	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:19:41.957449	\N
158	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:19:49.641229	\N
159	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:21:38.008425	\N
160	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:21:45.571877	\N
161	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:22:26.138797	\N
162	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:22:34.668576	\N
163	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:28:09.5726	\N
164	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:28:18.54286	\N
165	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:32:22.284101	\N
166	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:32:29.635245	\N
167	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:35:36.164679	\N
168	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:35:43.53472	\N
169	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:37:03.158608	\N
170	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:37:11.891771	\N
171	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:38:59.293498	\N
172	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:39:07.498537	\N
173	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:40:44.85069	\N
174	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:40:53.313912	\N
175	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:47:10.942183	\N
176	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:47:20.359999	\N
177	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:52:24.118687	\N
178	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:52:33.421458	\N
179	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:53:44.778006	\N
180	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:53:52.852687	\N
181	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:54:53.113283	\N
182	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:55:01.057464	\N
183	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-01 06:57:09.465955	\N
184	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 01:24:58.337458	\N
185	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 01:35:00.793905	\N
186	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 01:35:14.815286	\N
187	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 01:38:28.66368	\N
188	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 01:38:36.499708	\N
189	2	daily_attendance	create	1617	\N	{"id": "1617", "student_id": "693", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "غائب", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:11.956566	\N
190	2	daily_attendance	create	1618	\N	{"id": "1618", "student_id": "18", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:11.956566	\N
191	2	daily_attendance	create	1619	\N	{"id": "1619", "student_id": "14", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:11.956566	\N
192	2	daily_attendance	create	1620	\N	{"id": "1620", "student_id": "6", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:11.956566	\N
193	2	daily_attendance	create	1621	\N	{"id": "1621", "student_id": "7", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:11.956566	\N
194	2	daily_attendance	create	1622	\N	{"id": "1622", "student_id": "10", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:11.956566	\N
195	2	daily_attendance	create	1623	\N	{"id": "1623", "student_id": "12", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:11.956566	\N
196	2	daily_attendance	create	1624	\N	{"id": "1624", "student_id": "16", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:11.956566	\N
197	2	daily_attendance	create	1625	\N	{"id": "1625", "student_id": "3", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:11.956566	\N
198	2	daily_attendance	create	1626	\N	{"id": "1626", "student_id": "13", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:11.956566	\N
199	2	daily_attendance	create	1627	\N	{"id": "1627", "student_id": "17", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:11.956566	\N
200	2	daily_attendance	create	1628	\N	{"id": "1628", "student_id": "11", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:11.956566	\N
201	2	daily_attendance	create	1629	\N	{"id": "1629", "student_id": "4", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:11.956566	\N
202	2	daily_attendance	create	1630	\N	{"id": "1630", "student_id": "15", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:11.956566	\N
203	2	daily_attendance	create	1631	\N	{"id": "1631", "student_id": "5", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:11.956566	\N
204	2	daily_attendance	create	1632	\N	{"id": "1632", "student_id": "8", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:11.956566	\N
205	2	daily_attendance	delete	1625	{"id": "1625", "student_id": "3", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
206	2	daily_attendance	delete	1629	{"id": "1629", "student_id": "4", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
207	2	daily_attendance	delete	1631	{"id": "1631", "student_id": "5", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
208	2	daily_attendance	delete	1620	{"id": "1620", "student_id": "6", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
209	2	daily_attendance	delete	1621	{"id": "1621", "student_id": "7", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
210	2	daily_attendance	delete	1632	{"id": "1632", "student_id": "8", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
211	2	daily_attendance	delete	1622	{"id": "1622", "student_id": "10", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
212	2	daily_attendance	delete	1628	{"id": "1628", "student_id": "11", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
213	2	daily_attendance	delete	1623	{"id": "1623", "student_id": "12", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
214	2	daily_attendance	delete	1626	{"id": "1626", "student_id": "13", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
215	2	daily_attendance	delete	1619	{"id": "1619", "student_id": "14", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
216	2	daily_attendance	delete	1630	{"id": "1630", "student_id": "15", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
217	2	daily_attendance	delete	1624	{"id": "1624", "student_id": "16", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
218	2	daily_attendance	delete	1627	{"id": "1627", "student_id": "17", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
219	2	daily_attendance	delete	1618	{"id": "1618", "student_id": "18", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
220	2	daily_attendance	delete	1617	{"id": "1617", "student_id": "693", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "غائب", "notes": "", "created_at": "2026-09-02 01:40:11.956566", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
221	2	daily_attendance	create	1633	\N	{"id": "1633", "student_id": "693", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "غائب", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
222	2	daily_attendance	create	1634	\N	{"id": "1634", "student_id": "18", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "غائب", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
223	2	daily_attendance	create	1635	\N	{"id": "1635", "student_id": "14", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
224	2	daily_attendance	create	1636	\N	{"id": "1636", "student_id": "6", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
225	2	daily_attendance	create	1637	\N	{"id": "1637", "student_id": "7", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
226	2	daily_attendance	create	1638	\N	{"id": "1638", "student_id": "10", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
227	2	daily_attendance	create	1639	\N	{"id": "1639", "student_id": "12", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
228	2	daily_attendance	create	1640	\N	{"id": "1640", "student_id": "16", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
229	2	daily_attendance	create	1641	\N	{"id": "1641", "student_id": "3", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
230	2	daily_attendance	create	1642	\N	{"id": "1642", "student_id": "13", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
231	2	daily_attendance	create	1643	\N	{"id": "1643", "student_id": "17", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
232	2	daily_attendance	create	1644	\N	{"id": "1644", "student_id": "11", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
233	2	daily_attendance	create	1645	\N	{"id": "1645", "student_id": "4", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
234	2	daily_attendance	create	1646	\N	{"id": "1646", "student_id": "15", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
235	2	daily_attendance	create	1647	\N	{"id": "1647", "student_id": "5", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
236	2	daily_attendance	create	1648	\N	{"id": "1648", "student_id": "8", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:16.932532	\N
237	2	daily_attendance	delete	1641	{"id": "1641", "student_id": "3", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
238	2	daily_attendance	delete	1645	{"id": "1645", "student_id": "4", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
239	2	daily_attendance	delete	1647	{"id": "1647", "student_id": "5", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
240	2	daily_attendance	delete	1636	{"id": "1636", "student_id": "6", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
241	2	daily_attendance	delete	1637	{"id": "1637", "student_id": "7", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
242	2	daily_attendance	delete	1648	{"id": "1648", "student_id": "8", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
243	2	daily_attendance	delete	1638	{"id": "1638", "student_id": "10", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
244	2	daily_attendance	delete	1644	{"id": "1644", "student_id": "11", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
245	2	daily_attendance	delete	1639	{"id": "1639", "student_id": "12", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
246	2	daily_attendance	delete	1642	{"id": "1642", "student_id": "13", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
247	2	daily_attendance	delete	1635	{"id": "1635", "student_id": "14", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
248	2	daily_attendance	delete	1646	{"id": "1646", "student_id": "15", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
249	2	daily_attendance	delete	1640	{"id": "1640", "student_id": "16", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
250	2	daily_attendance	delete	1643	{"id": "1643", "student_id": "17", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
251	2	daily_attendance	delete	1634	{"id": "1634", "student_id": "18", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "غائب", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
252	2	daily_attendance	delete	1633	{"id": "1633", "student_id": "693", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "غائب", "notes": "", "created_at": "2026-09-02 01:40:16.932532", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
253	2	daily_attendance	create	1649	\N	{"id": "1649", "student_id": "693", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "غائب", "notes": "e", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
254	2	daily_attendance	create	1650	\N	{"id": "1650", "student_id": "18", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "غائب", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
255	2	daily_attendance	create	1651	\N	{"id": "1651", "student_id": "14", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
256	2	daily_attendance	create	1652	\N	{"id": "1652", "student_id": "6", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
257	2	daily_attendance	create	1653	\N	{"id": "1653", "student_id": "7", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
258	2	daily_attendance	create	1654	\N	{"id": "1654", "student_id": "10", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
259	2	daily_attendance	create	1655	\N	{"id": "1655", "student_id": "12", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
260	2	daily_attendance	create	1656	\N	{"id": "1656", "student_id": "16", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
261	2	daily_attendance	create	1657	\N	{"id": "1657", "student_id": "3", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
262	2	daily_attendance	create	1658	\N	{"id": "1658", "student_id": "13", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
263	2	daily_attendance	create	1659	\N	{"id": "1659", "student_id": "17", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
264	2	daily_attendance	create	1660	\N	{"id": "1660", "student_id": "11", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
265	2	daily_attendance	create	1661	\N	{"id": "1661", "student_id": "4", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
266	2	daily_attendance	create	1662	\N	{"id": "1662", "student_id": "15", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
267	2	daily_attendance	create	1663	\N	{"id": "1663", "student_id": "5", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
268	2	daily_attendance	create	1664	\N	{"id": "1664", "student_id": "8", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:23.88036	\N
269	2	daily_attendance	delete	1657	{"id": "1657", "student_id": "3", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
270	2	daily_attendance	delete	1661	{"id": "1661", "student_id": "4", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
271	2	daily_attendance	delete	1663	{"id": "1663", "student_id": "5", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
272	2	daily_attendance	delete	1652	{"id": "1652", "student_id": "6", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
273	2	daily_attendance	delete	1653	{"id": "1653", "student_id": "7", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
274	2	daily_attendance	delete	1664	{"id": "1664", "student_id": "8", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
275	2	daily_attendance	delete	1654	{"id": "1654", "student_id": "10", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
276	2	daily_attendance	delete	1660	{"id": "1660", "student_id": "11", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
277	2	daily_attendance	delete	1655	{"id": "1655", "student_id": "12", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
278	2	daily_attendance	delete	1658	{"id": "1658", "student_id": "13", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
279	2	daily_attendance	delete	1651	{"id": "1651", "student_id": "14", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
280	2	daily_attendance	delete	1662	{"id": "1662", "student_id": "15", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
281	2	daily_attendance	delete	1656	{"id": "1656", "student_id": "16", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
282	2	daily_attendance	delete	1659	{"id": "1659", "student_id": "17", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
283	2	daily_attendance	delete	1650	{"id": "1650", "student_id": "18", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "غائب", "notes": "", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
284	2	daily_attendance	delete	1649	{"id": "1649", "student_id": "693", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "غائب", "notes": "e", "created_at": "2026-09-02 01:40:23.880360", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
285	2	daily_attendance	create	1665	\N	{"id": "1665", "student_id": "693", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "غائب", "notes": "ee", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
286	2	daily_attendance	create	1666	\N	{"id": "1666", "student_id": "18", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "غائب", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
287	2	daily_attendance	create	1667	\N	{"id": "1667", "student_id": "14", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
288	2	daily_attendance	create	1668	\N	{"id": "1668", "student_id": "6", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
289	2	daily_attendance	create	1669	\N	{"id": "1669", "student_id": "7", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
290	2	daily_attendance	create	1670	\N	{"id": "1670", "student_id": "10", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
291	2	daily_attendance	create	1671	\N	{"id": "1671", "student_id": "12", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
292	2	daily_attendance	create	1672	\N	{"id": "1672", "student_id": "16", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
293	2	daily_attendance	create	1673	\N	{"id": "1673", "student_id": "3", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
294	2	daily_attendance	create	1674	\N	{"id": "1674", "student_id": "13", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
295	2	daily_attendance	create	1675	\N	{"id": "1675", "student_id": "17", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
296	2	daily_attendance	create	1676	\N	{"id": "1676", "student_id": "11", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
297	2	daily_attendance	create	1677	\N	{"id": "1677", "student_id": "4", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
298	2	daily_attendance	create	1678	\N	{"id": "1678", "student_id": "15", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
299	2	daily_attendance	create	1679	\N	{"id": "1679", "student_id": "5", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
300	2	daily_attendance	create	1680	\N	{"id": "1680", "student_id": "8", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:40:37.034666	\N
301	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 01:43:00.044318	\N
302	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 01:43:07.576278	\N
303	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 01:46:34.214675	\N
304	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 01:46:44.476278	\N
305	2	daily_attendance	delete	1665	{"id": "1665", "student_id": "693", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "غائب", "notes": "ee", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
306	2	daily_attendance	delete	1666	{"id": "1666", "student_id": "18", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "غائب", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
307	2	daily_attendance	delete	1667	{"id": "1667", "student_id": "14", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
308	2	daily_attendance	delete	1668	{"id": "1668", "student_id": "6", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
309	2	daily_attendance	delete	1669	{"id": "1669", "student_id": "7", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
310	2	daily_attendance	delete	1670	{"id": "1670", "student_id": "10", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
311	2	daily_attendance	delete	1671	{"id": "1671", "student_id": "12", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
312	2	daily_attendance	delete	1672	{"id": "1672", "student_id": "16", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
313	2	daily_attendance	delete	1673	{"id": "1673", "student_id": "3", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
314	2	daily_attendance	delete	1674	{"id": "1674", "student_id": "13", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
315	2	daily_attendance	delete	1675	{"id": "1675", "student_id": "17", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
316	2	daily_attendance	delete	1676	{"id": "1676", "student_id": "11", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
317	2	daily_attendance	delete	1677	{"id": "1677", "student_id": "4", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
439	2	تسجيل الدخول	login	\N	\N	\N	10.13.84.80	عبود	2026-09-02 03:52:37.751572	\N
440	2	تسجيل الخروج	logout	\N	\N	\N	10.13.84.80	عبود	2026-09-02 03:54:10.868914	\N
318	2	daily_attendance	delete	1678	{"id": "1678", "student_id": "15", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
319	2	daily_attendance	delete	1679	{"id": "1679", "student_id": "5", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
320	2	daily_attendance	delete	1680	{"id": "1680", "student_id": "8", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:40:37.034666", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
321	2	daily_attendance	create	1681	\N	{"id": "1681", "student_id": "693", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "ee", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
322	2	daily_attendance	create	1682	\N	{"id": "1682", "student_id": "18", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "غائب", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
323	2	daily_attendance	create	1683	\N	{"id": "1683", "student_id": "14", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
324	2	daily_attendance	create	1684	\N	{"id": "1684", "student_id": "6", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
325	2	daily_attendance	create	1685	\N	{"id": "1685", "student_id": "7", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
326	2	daily_attendance	create	1686	\N	{"id": "1686", "student_id": "10", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
327	2	daily_attendance	create	1687	\N	{"id": "1687", "student_id": "12", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
328	2	daily_attendance	create	1688	\N	{"id": "1688", "student_id": "16", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
329	2	daily_attendance	create	1689	\N	{"id": "1689", "student_id": "3", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
330	2	daily_attendance	create	1690	\N	{"id": "1690", "student_id": "13", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
331	2	daily_attendance	create	1691	\N	{"id": "1691", "student_id": "17", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
332	2	daily_attendance	create	1692	\N	{"id": "1692", "student_id": "11", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
333	2	daily_attendance	create	1693	\N	{"id": "1693", "student_id": "4", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
334	2	daily_attendance	create	1694	\N	{"id": "1694", "student_id": "15", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
335	2	daily_attendance	create	1695	\N	{"id": "1695", "student_id": "5", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
336	2	daily_attendance	create	1696	\N	{"id": "1696", "student_id": "8", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 01:47:24.219282	\N
337	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 01:47:50.207352	\N
338	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 01:47:56.497912	\N
339	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 01:49:18.426465	\N
340	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 01:49:25.083119	\N
341	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 01:57:53.833352	\N
342	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 01:58:01.234403	\N
343	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:02:19.921734	\N
344	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:02:26.593633	\N
345	2	daily_attendance	delete	1681	{"id": "1681", "student_id": "693", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "ee", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
346	2	daily_attendance	delete	1682	{"id": "1682", "student_id": "18", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "غائب", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
441	2	تسجيل الدخول	login	\N	\N	\N	10.13.84.80	عبود	2026-09-02 03:54:17.296421	\N
347	2	daily_attendance	delete	1683	{"id": "1683", "student_id": "14", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
348	2	daily_attendance	delete	1684	{"id": "1684", "student_id": "6", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
349	2	daily_attendance	delete	1685	{"id": "1685", "student_id": "7", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
350	2	daily_attendance	delete	1686	{"id": "1686", "student_id": "10", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
351	2	daily_attendance	delete	1687	{"id": "1687", "student_id": "12", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
352	2	daily_attendance	delete	1688	{"id": "1688", "student_id": "16", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
353	2	daily_attendance	delete	1689	{"id": "1689", "student_id": "3", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
354	2	daily_attendance	delete	1690	{"id": "1690", "student_id": "13", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
355	2	daily_attendance	delete	1691	{"id": "1691", "student_id": "17", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
356	2	daily_attendance	delete	1692	{"id": "1692", "student_id": "11", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
357	2	daily_attendance	delete	1693	{"id": "1693", "student_id": "4", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
358	2	daily_attendance	delete	1694	{"id": "1694", "student_id": "15", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
359	2	daily_attendance	delete	1695	{"id": "1695", "student_id": "5", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
360	2	daily_attendance	delete	1696	{"id": "1696", "student_id": "8", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 01:47:24.219282", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
361	2	daily_attendance	create	1697	\N	{"id": "1697", "student_id": "693", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "ee", "created_at": "2026-09-02 02:03:01.928854", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
362	2	daily_attendance	create	1698	\N	{"id": "1698", "student_id": "18", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "غائب", "notes": "", "created_at": "2026-09-02 02:03:01.928854", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
363	2	daily_attendance	create	1699	\N	{"id": "1699", "student_id": "14", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 02:03:01.928854", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
364	2	daily_attendance	create	1700	\N	{"id": "1700", "student_id": "6", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 02:03:01.928854", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
365	2	daily_attendance	create	1701	\N	{"id": "1701", "student_id": "7", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 02:03:01.928854", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
366	2	daily_attendance	create	1702	\N	{"id": "1702", "student_id": "10", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 02:03:01.928854", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
367	2	daily_attendance	create	1703	\N	{"id": "1703", "student_id": "12", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 02:03:01.928854", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
368	2	daily_attendance	create	1704	\N	{"id": "1704", "student_id": "16", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 02:03:01.928854", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
369	2	daily_attendance	create	1705	\N	{"id": "1705", "student_id": "3", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 02:03:01.928854", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
370	2	daily_attendance	create	1706	\N	{"id": "1706", "student_id": "13", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 02:03:01.928854", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
371	2	daily_attendance	create	1707	\N	{"id": "1707", "student_id": "17", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 02:03:01.928854", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
372	2	daily_attendance	create	1708	\N	{"id": "1708", "student_id": "11", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 02:03:01.928854", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
373	2	daily_attendance	create	1709	\N	{"id": "1709", "student_id": "4", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 02:03:01.928854", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
374	2	daily_attendance	create	1710	\N	{"id": "1710", "student_id": "15", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 02:03:01.928854", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
375	2	daily_attendance	create	1711	\N	{"id": "1711", "student_id": "5", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 02:03:01.928854", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
376	2	daily_attendance	create	1712	\N	{"id": "1712", "student_id": "8", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "attendance_date": "2026-09-02", "status": "حاضر", "notes": "", "created_at": "2026-09-02 02:03:01.928854", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:03:01.928854	\N
377	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:04:23.262462	\N
378	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:04:29.243055	\N
379	2	weekly_schedules	create	1	\N	{"id": "1", "academic_year_id": "1", "term": "1", "grade_id": "1", "section_id": "1", "day_of_week": "saturday", "period_number": "1", "subject_id": "1", "teacher_id": "None", "created_at": "2026-09-02 02:05:46.774226", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:05:46.774226	\N
380	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:07:31.079055	\N
381	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:07:37.791926	\N
382	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:11:50.102461	\N
383	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:11:58.552096	\N
384	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:13:04.424769	\N
385	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:13:11.352494	\N
386	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:20:54.057513	\N
387	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:21:01.129696	\N
388	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:22:57.741502	\N
389	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:23:05.081086	\N
390	2	weekly_schedules	create	2	\N	{"id": "2", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "saturday", "period_number": "1", "subject_id": "1", "teacher_id": "None", "created_at": "2026-09-02 02:24:36.884187", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:24:36.884187	\N
391	2	weekly_schedules	create	3	\N	{"id": "3", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "sunday", "period_number": "1", "subject_id": "2", "teacher_id": "None", "created_at": "2026-09-02 02:24:36.884187", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:24:36.884187	\N
392	2	weekly_schedules	delete	1	{"id": "1", "academic_year_id": "1", "term": "1", "grade_id": "1", "section_id": "1", "day_of_week": "saturday", "period_number": "1", "subject_id": "1", "teacher_id": "None", "created_at": "2026-09-02 02:05:46.774226", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:24:53.452845	\N
393	2	weekly_schedules	create	4	\N	{"id": "4", "academic_year_id": "1", "term": "1", "grade_id": "1", "section_id": "1", "day_of_week": "saturday", "period_number": "1", "subject_id": "1", "teacher_id": "None", "created_at": "2026-09-02 02:24:53.452845", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:24:53.452845	\N
394	2	weekly_schedules	create	5	\N	{"id": "5", "academic_year_id": "1", "term": "1", "grade_id": "1", "section_id": "1", "day_of_week": "monday", "period_number": "1", "subject_id": "8", "teacher_id": "None", "created_at": "2026-09-02 02:24:53.452845", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:24:53.452845	\N
395	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:31:50.756404	\N
396	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:31:58.101926	\N
397	2	weekly_schedules	delete	2	{"id": "2", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "saturday", "period_number": "1", "subject_id": "1", "teacher_id": "None", "created_at": "2026-09-02 02:24:36.884187", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:33:20.243183	\N
398	2	weekly_schedules	delete	3	{"id": "3", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "sunday", "period_number": "1", "subject_id": "2", "teacher_id": "None", "created_at": "2026-09-02 02:24:36.884187", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:33:20.243183	\N
399	2	weekly_schedules	create	6	\N	{"id": "6", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "saturday", "period_number": "1", "subject_id": "1", "teacher_id": "None", "created_at": "2026-09-02 02:33:20.243183", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:33:20.243183	\N
400	2	weekly_schedules	create	7	\N	{"id": "7", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "monday", "period_number": "1", "subject_id": "8", "teacher_id": "None", "created_at": "2026-09-02 02:33:20.243183", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:33:20.243183	\N
401	2	weekly_schedules	create	8	\N	{"id": "8", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "tuesday", "period_number": "1", "subject_id": "2", "teacher_id": "None", "created_at": "2026-09-02 02:33:20.243183", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:33:20.243183	\N
402	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:40:20.050985	\N
403	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:40:26.512605	\N
404	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:49:25.387299	\N
405	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:49:32.56223	\N
406	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:53:39.716765	\N
407	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:53:46.648172	\N
442	2	تسجيل الخروج	logout	\N	\N	\N	10.13.84.80	عبود	2026-09-02 03:58:56.194989	\N
408	2	weekly_schedules	delete	7	{"id": "7", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "monday", "period_number": "1", "subject_id": "8", "teacher_id": "None", "created_at": "2026-09-02 02:33:20.243183", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:56:37.684737	\N
409	2	weekly_schedules	delete	6	{"id": "6", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "saturday", "period_number": "1", "subject_id": "1", "teacher_id": "None", "created_at": "2026-09-02 02:33:20.243183", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:56:37.684737	\N
410	2	weekly_schedules	delete	8	{"id": "8", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "tuesday", "period_number": "1", "subject_id": "2", "teacher_id": "None", "created_at": "2026-09-02 02:33:20.243183", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 02:56:37.684737	\N
411	2	weekly_schedules	create	9	\N	{"id": "9", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "saturday", "period_number": "1", "subject_id": "1", "teacher_id": "None", "created_at": "2026-09-02 02:56:37.684737", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:56:37.684737	\N
412	2	weekly_schedules	create	10	\N	{"id": "10", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "sunday", "period_number": "1", "subject_id": "10", "teacher_id": "None", "created_at": "2026-09-02 02:56:37.684737", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:56:37.684737	\N
413	2	weekly_schedules	create	11	\N	{"id": "11", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "monday", "period_number": "1", "subject_id": "8", "teacher_id": "None", "created_at": "2026-09-02 02:56:37.684737", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:56:37.684737	\N
414	2	weekly_schedules	create	12	\N	{"id": "12", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "tuesday", "period_number": "1", "subject_id": "2", "teacher_id": "None", "created_at": "2026-09-02 02:56:37.684737", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 02:56:37.684737	\N
415	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:56:53.181729	\N
416	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 02:57:00.150023	\N
417	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 03:00:12.902025	\N
418	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 03:00:27.112988	\N
419	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 03:02:06.718133	\N
420	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 03:02:14.027611	\N
421	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 03:04:01.226182	\N
422	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 03:04:07.474786	\N
423	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 03:04:42.213111	\N
424	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 03:04:48.373496	\N
425	2	monthly_exam_schedules	create	1	\N	{"id": "1", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "1", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 03:09:38.481584", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 03:09:38.481584	\N
426	2	monthly_exam_schedules	create	2	\N	{"id": "2", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "2", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 03:09:38.481584", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 03:09:38.481584	\N
427	2	monthly_exam_schedules	create	3	\N	{"id": "3", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "3", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 03:09:38.481584", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 03:09:38.481584	\N
428	2	monthly_exam_schedules	create	4	\N	{"id": "4", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "4", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 03:09:38.481584", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 03:09:38.481584	\N
429	2	monthly_exam_schedules	create	5	\N	{"id": "5", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "5", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 03:09:38.481584", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 03:09:38.481584	\N
430	2	monthly_exam_schedules	create	6	\N	{"id": "6", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "6", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 03:09:38.481584", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 03:09:38.481584	\N
431	2	monthly_exam_schedules	create	7	\N	{"id": "7", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "7", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 03:09:38.481584", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 03:09:38.481584	\N
432	2	monthly_exam_schedules	create	8	\N	{"id": "8", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "8", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 03:09:38.481584", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 03:09:38.481584	\N
433	2	monthly_exam_schedules	create	9	\N	{"id": "9", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "9", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 03:09:38.481584", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 03:09:38.481584	\N
434	2	monthly_exam_schedules	create	10	\N	{"id": "10", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "10", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 03:09:38.481584", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 03:09:38.481584	\N
435	2	receipts	create	120	\N	{"id": "120", "receipt_number": "RCV-20260902033156", "student_id": "4", "installment_id": "274", "payment_target": "current_fee", "amount_paid": "10143.0", "payment_date": "2026-09-02 03:32:33.215659", "payment_method": "نقداً", "reference_number": "None", "notes": "None", "created_by_user_id": "2", "status": "نشط", "cancellation_reason": "None", "cancelled_at": "None", "created_at": "2026-09-02 03:32:33.215659", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 03:32:33.215659	\N
436	2	تسجيل الخروج	logout	\N	\N	\N	10.13.84.80	عبود	2026-09-02 03:36:59.880719	\N
437	2	تسجيل الدخول	login	\N	\N	\N	10.13.84.80	عبود	2026-09-02 03:37:23.159336	\N
444	2	تسجيل الخروج	logout	\N	\N	\N	10.13.84.80	عبود	2026-09-02 04:01:56.878779	\N
445	2	تسجيل الدخول	login	\N	\N	\N	10.13.84.80	عبود	2026-09-02 04:02:03.539859	\N
446	2	payroll_records	create	91	\N	{"id": "91", "employee_id": "1", "month": "10", "year": "2026", "basic_salary": "0.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "0.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
447	2	payroll_records	create	92	\N	{"id": "92", "employee_id": "10", "month": "10", "year": "2026", "basic_salary": "147433.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "147433.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
448	2	payroll_records	create	93	\N	{"id": "93", "employee_id": "5", "month": "10", "year": "2026", "basic_salary": "111926.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "36641.92", "net_salary": "75284.08", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
449	2	payroll_records	create	94	\N	{"id": "94", "employee_id": "6", "month": "10", "year": "2026", "basic_salary": "236904.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "45988.00", "net_salary": "190916.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
450	2	payroll_records	create	95	\N	{"id": "95", "employee_id": "8", "month": "10", "year": "2026", "basic_salary": "227081.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "227081.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
451	2	payroll_records	create	96	\N	{"id": "96", "employee_id": "11", "month": "10", "year": "2026", "basic_salary": "127427.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "31260.25", "net_salary": "96166.75", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
452	2	payroll_records	create	97	\N	{"id": "97", "employee_id": "12", "month": "10", "year": "2026", "basic_salary": "248985.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "21407.22", "net_salary": "227577.78", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
453	2	payroll_records	create	98	\N	{"id": "98", "employee_id": "13", "month": "10", "year": "2026", "basic_salary": "128636.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "128636.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
454	2	payroll_records	create	99	\N	{"id": "99", "employee_id": "14", "month": "10", "year": "2026", "basic_salary": "212050.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "16732.38", "net_salary": "195317.62", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
455	2	payroll_records	create	100	\N	{"id": "100", "employee_id": "15", "month": "10", "year": "2026", "basic_salary": "163636.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "163636.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
456	2	payroll_records	create	101	\N	{"id": "101", "employee_id": "16", "month": "10", "year": "2026", "basic_salary": "123808.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "123808.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
457	2	payroll_records	create	102	\N	{"id": "102", "employee_id": "18", "month": "10", "year": "2026", "basic_salary": "100303.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "100303.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
458	2	payroll_records	create	103	\N	{"id": "103", "employee_id": "19", "month": "10", "year": "2026", "basic_salary": "168836.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "168836.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
459	2	payroll_records	create	104	\N	{"id": "104", "employee_id": "20", "month": "10", "year": "2026", "basic_salary": "118026.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "118026.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
460	2	payroll_records	create	105	\N	{"id": "105", "employee_id": "22", "month": "10", "year": "2026", "basic_salary": "97649.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "97649.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
461	2	payroll_records	create	106	\N	{"id": "106", "employee_id": "23", "month": "10", "year": "2026", "basic_salary": "117980.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "117980.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
462	2	payroll_records	create	107	\N	{"id": "107", "employee_id": "24", "month": "10", "year": "2026", "basic_salary": "169821.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "169821.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
463	2	payroll_records	create	108	\N	{"id": "108", "employee_id": "25", "month": "10", "year": "2026", "basic_salary": "167367.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "167367.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
526	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 05:54:11.394655	\N
527	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 05:54:22.450725	\N
464	2	payroll_records	create	109	\N	{"id": "109", "employee_id": "27", "month": "10", "year": "2026", "basic_salary": "197153.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "197153.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
465	2	payroll_records	create	110	\N	{"id": "110", "employee_id": "28", "month": "10", "year": "2026", "basic_salary": "173838.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "173838.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
466	2	payroll_records	create	111	\N	{"id": "111", "employee_id": "29", "month": "10", "year": "2026", "basic_salary": "213489.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "213489.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
467	2	payroll_records	create	112	\N	{"id": "112", "employee_id": "30", "month": "10", "year": "2026", "basic_salary": "129386.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "129386.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
468	2	payroll_records	create	113	\N	{"id": "113", "employee_id": "31", "month": "10", "year": "2026", "basic_salary": "229136.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "229136.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
469	2	payroll_records	create	114	\N	{"id": "114", "employee_id": "34", "month": "10", "year": "2026", "basic_salary": "170565.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "170565.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
470	2	payroll_records	create	115	\N	{"id": "115", "employee_id": "32", "month": "10", "year": "2026", "basic_salary": "91759.00", "total_allowances": "0.00", "total_deductions": "0.00", "loan_deduction": "0.00", "net_salary": "91759.00", "payment_status": "معلق", "payment_date": "None", "created_at": "2026-09-02 04:05:04.463450", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:05:04.46345	\N
471	2	employee_loans	create	9	\N	{"id": "9", "employee_id": "1", "total_loan_amount": "13.0", "monthly_deduction": "9.0", "status": "مستمرة", "loan_date": "2026-09-02", "reason": "None", "remaining_amount": "0.00", "created_at": "2026-09-02 04:07:06.163230", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:07:06.16323	\N
472	2	تسجيل الخروج	logout	\N	\N	\N	10.13.84.80	عبود	2026-09-02 04:12:49.641379	\N
473	2	تسجيل الدخول	login	\N	\N	\N	10.13.84.80	عبود	2026-09-02 04:13:00.394834	\N
474	2	term_exam_scores	create	201	\N	{"id": "201", "student_id": "693", "academic_year_id": "1", "grade_id": "1", "section_id": "1", "subject_id": "1", "term": "1", "exam_score": "3.0", "created_at": "2026-09-02 04:14:05.053421", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:14:05.053421	\N
475	2	تسجيل الخروج	logout	\N	\N	\N	10.13.84.80	عبود	2026-09-02 04:17:13.565652	\N
476	2	تسجيل الدخول	login	\N	\N	\N	10.13.84.80	عبود	2026-09-02 04:17:19.725812	\N
477	2	تسجيل الخروج	logout	\N	\N	\N	10.13.84.80	عبود	2026-09-02 04:31:17.358053	\N
478	2	تسجيل الدخول	login	\N	\N	\N	10.13.84.80	عبود	2026-09-02 04:31:35.484091	\N
479	2	weekly_schedules	delete	5	{"id": "5", "academic_year_id": "1", "term": "1", "grade_id": "1", "section_id": "1", "day_of_week": "monday", "period_number": "1", "subject_id": "8", "teacher_id": "None", "created_at": "2026-09-02 02:24:53.452845", "updated_at": "None"}	\N	10.13.84.80	عبود	2026-09-02 04:32:05.434719	\N
480	2	weekly_schedules	delete	4	{"id": "4", "academic_year_id": "1", "term": "1", "grade_id": "1", "section_id": "1", "day_of_week": "saturday", "period_number": "1", "subject_id": "1", "teacher_id": "None", "created_at": "2026-09-02 02:24:53.452845", "updated_at": "None"}	\N	10.13.84.80	عبود	2026-09-02 04:32:05.434719	\N
481	2	weekly_schedules	create	13	\N	{"id": "13", "academic_year_id": "1", "term": "1", "grade_id": "1", "section_id": "1", "day_of_week": "saturday", "period_number": "1", "subject_id": "1", "teacher_id": "None", "created_at": "2026-09-02 04:32:05.434719", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:32:05.434719	\N
482	2	weekly_schedules	create	14	\N	{"id": "14", "academic_year_id": "1", "term": "1", "grade_id": "1", "section_id": "1", "day_of_week": "monday", "period_number": "1", "subject_id": "5", "teacher_id": "None", "created_at": "2026-09-02 04:32:05.434719", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:32:05.434719	\N
483	2	weekly_schedules	delete	11	{"id": "11", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "monday", "period_number": "1", "subject_id": "8", "teacher_id": "None", "created_at": "2026-09-02 02:56:37.684737", "updated_at": "None"}	\N	10.13.84.80	عبود	2026-09-02 04:32:47.453395	\N
484	2	weekly_schedules	delete	9	{"id": "9", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "saturday", "period_number": "1", "subject_id": "1", "teacher_id": "None", "created_at": "2026-09-02 02:56:37.684737", "updated_at": "None"}	\N	10.13.84.80	عبود	2026-09-02 04:32:47.453395	\N
485	2	weekly_schedules	delete	10	{"id": "10", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "sunday", "period_number": "1", "subject_id": "10", "teacher_id": "None", "created_at": "2026-09-02 02:56:37.684737", "updated_at": "None"}	\N	10.13.84.80	عبود	2026-09-02 04:32:47.453395	\N
486	2	weekly_schedules	delete	12	{"id": "12", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "tuesday", "period_number": "1", "subject_id": "2", "teacher_id": "None", "created_at": "2026-09-02 02:56:37.684737", "updated_at": "None"}	\N	10.13.84.80	عبود	2026-09-02 04:32:47.453395	\N
487	2	weekly_schedules	create	15	\N	{"id": "15", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "saturday", "period_number": "1", "subject_id": "1", "teacher_id": "None", "created_at": "2026-09-02 04:32:47.453395", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:32:47.453395	\N
488	2	weekly_schedules	create	16	\N	{"id": "16", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "sunday", "period_number": "1", "subject_id": "5", "teacher_id": "None", "created_at": "2026-09-02 04:32:47.453395", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:32:47.453395	\N
489	2	weekly_schedules	create	17	\N	{"id": "17", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "monday", "period_number": "1", "subject_id": "4", "teacher_id": "None", "created_at": "2026-09-02 04:32:47.453395", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:32:47.453395	\N
490	2	weekly_schedules	create	18	\N	{"id": "18", "academic_year_id": "1", "term": "2", "grade_id": "1", "section_id": "1", "day_of_week": "tuesday", "period_number": "1", "subject_id": "2", "teacher_id": "None", "created_at": "2026-09-02 04:32:47.453395", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:32:47.453395	\N
491	2	monthly_exam_schedules	delete	1	{"id": "1", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "1", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 03:09:38.481584", "updated_at": "None"}	\N	10.13.84.80	عبود	2026-09-02 04:32:58.376224	\N
492	2	monthly_exam_schedules	delete	2	{"id": "2", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "2", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 03:09:38.481584", "updated_at": "None"}	\N	10.13.84.80	عبود	2026-09-02 04:32:58.376224	\N
493	2	monthly_exam_schedules	delete	3	{"id": "3", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "3", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 03:09:38.481584", "updated_at": "None"}	\N	10.13.84.80	عبود	2026-09-02 04:32:58.376224	\N
494	2	monthly_exam_schedules	delete	4	{"id": "4", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "4", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 03:09:38.481584", "updated_at": "None"}	\N	10.13.84.80	عبود	2026-09-02 04:32:58.376224	\N
495	2	monthly_exam_schedules	delete	5	{"id": "5", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "5", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 03:09:38.481584", "updated_at": "None"}	\N	10.13.84.80	عبود	2026-09-02 04:32:58.376224	\N
496	2	monthly_exam_schedules	delete	6	{"id": "6", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "6", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 03:09:38.481584", "updated_at": "None"}	\N	10.13.84.80	عبود	2026-09-02 04:32:58.376224	\N
497	2	monthly_exam_schedules	delete	7	{"id": "7", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "7", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 03:09:38.481584", "updated_at": "None"}	\N	10.13.84.80	عبود	2026-09-02 04:32:58.376224	\N
498	2	monthly_exam_schedules	delete	8	{"id": "8", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "8", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 03:09:38.481584", "updated_at": "None"}	\N	10.13.84.80	عبود	2026-09-02 04:32:58.376224	\N
499	2	monthly_exam_schedules	delete	9	{"id": "9", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "9", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 03:09:38.481584", "updated_at": "None"}	\N	10.13.84.80	عبود	2026-09-02 04:32:58.376224	\N
500	2	monthly_exam_schedules	delete	10	{"id": "10", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "10", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 03:09:38.481584", "updated_at": "None"}	\N	10.13.84.80	عبود	2026-09-02 04:32:58.376224	\N
501	2	monthly_exam_schedules	create	11	\N	{"id": "11", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "2", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 04:32:58.376224", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:32:58.376224	\N
502	2	monthly_exam_schedules	create	12	\N	{"id": "12", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "5", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 04:32:58.376224", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:32:58.376224	\N
503	2	monthly_exam_schedules	create	13	\N	{"id": "13", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "1", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 04:32:58.376224", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:32:58.376224	\N
504	2	monthly_exam_schedules	create	14	\N	{"id": "14", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "4", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 04:32:58.376224", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:32:58.376224	\N
505	2	monthly_exam_schedules	create	15	\N	{"id": "15", "academic_year_id": "1", "term": "1", "month": "1", "grade_id": "1", "section_id": "1", "subject_id": "3", "exam_date": "2026-09-02", "day_name": "السبت", "period_number": "1", "created_at": "2026-09-02 04:32:58.376224", "updated_at": "None"}	10.13.84.80	عبود	2026-09-02 04:32:58.376224	\N
506	2	تسجيل الخروج	logout	\N	\N	\N	10.13.84.80	عبود	2026-09-02 04:40:59.988562	\N
507	2	تسجيل الدخول	login	\N	\N	\N	10.13.84.80	عبود	2026-09-02 04:41:44.319639	\N
508	2	تسجيل الخروج	logout	\N	\N	\N	10.13.84.80	عبود	2026-09-02 04:41:48.209765	\N
509	2	تسجيل الدخول	login	\N	\N	\N	10.13.84.80	عبود	2026-09-02 04:41:58.126825	\N
510	2	تسجيل الخروج	logout	\N	\N	\N	10.13.84.80	عبود	2026-09-02 04:45:57.295816	\N
511	2	تسجيل الدخول	login	\N	\N	\N	10.13.84.80	عبود	2026-09-02 04:46:04.985798	\N
512	2	تسجيل الخروج	logout	\N	\N	\N	10.13.84.80	عبود	2026-09-02 04:48:40.000087	\N
513	2	تسجيل الدخول	login	\N	\N	\N	10.13.84.80	عبود	2026-09-02 04:48:50.346122	\N
514	2	تسجيل الخروج	logout	\N	\N	\N	10.13.84.80	عبود	2026-09-02 04:59:32.805755	\N
515	2	تسجيل الدخول	login	\N	\N	\N	10.13.84.80	عبود	2026-09-02 04:59:41.048753	\N
516	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 05:19:40.904847	\N
517	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 05:19:49.191289	\N
518	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 05:34:37.566878	\N
519	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 05:34:46.142749	\N
520	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 05:39:38.454371	\N
521	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 05:39:55.073714	\N
522	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 05:43:25.784468	\N
523	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 05:43:35.332207	\N
524	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 05:51:25.75499	\N
525	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 05:51:35.548714	\N
528	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 05:56:04.188083	\N
529	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 05:58:39.308287	\N
530	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 05:59:01.432152	\N
531	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:03:18.344513	\N
532	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:03:27.345354	\N
533	2	fee_installments	delete	270	{"id": "270", "student_fee_id": "3", "installment_type": "regular", "installment_number": "1", "installment_name": "d", "amount": "6087.00", "due_date": "2026-10-01", "is_paid": "False", "paid_amount": "0.00", "created_at": "2026-09-01 04:17:07.919896", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 06:07:02.640626	\N
534	2	fee_installments	delete	271	{"id": "271", "student_fee_id": "3", "installment_type": "regular", "installment_number": "2", "installment_name": "قسط 2", "amount": "6087.00", "due_date": "2026-11-01", "is_paid": "False", "paid_amount": "0.00", "created_at": "2026-09-01 04:17:07.919896", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 06:07:02.640626	\N
535	2	fee_installments	delete	272	{"id": "272", "student_fee_id": "3", "installment_type": "regular", "installment_number": "3", "installment_name": "قسط 3", "amount": "6087.00", "due_date": "2026-12-01", "is_paid": "False", "paid_amount": "0.00", "created_at": "2026-09-01 04:17:07.919896", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-02 06:07:02.640626	\N
536	2	fee_installments	create	275	\N	{"id": "275", "student_fee_id": "3", "installment_type": "regular", "installment_number": "1", "installment_name": "قسط 1", "amount": "6087.0", "due_date": "2026-10-02", "is_paid": "False", "paid_amount": "0.00", "created_at": "2026-09-02 06:07:02.640626", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 06:07:02.640626	\N
537	2	fee_installments	create	276	\N	{"id": "276", "student_fee_id": "3", "installment_type": "regular", "installment_number": "2", "installment_name": "قسط 2", "amount": "6087.0", "due_date": "2026-11-02", "is_paid": "False", "paid_amount": "0.00", "created_at": "2026-09-02 06:07:02.640626", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 06:07:02.640626	\N
538	2	fee_installments	create	277	\N	{"id": "277", "student_fee_id": "3", "installment_type": "regular", "installment_number": "3", "installment_name": "قسط 3", "amount": "6087.0", "due_date": "2026-12-02", "is_paid": "False", "paid_amount": "0.00", "created_at": "2026-09-02 06:07:02.640626", "updated_at": "None"}	192.168.56.1	عبود	2026-09-02 06:07:02.640626	\N
539	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:15:59.259616	\N
540	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:16:07.410876	\N
541	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:18:52.201684	\N
542	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:19:00.100651	\N
543	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:19:46.019631	\N
544	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:19:53.091427	\N
545	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:21:49.288831	\N
546	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:21:58.9402	\N
547	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:23:19.860981	\N
548	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:23:27.539067	\N
549	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:25:43.720362	\N
550	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:25:52.075546	\N
551	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:30:16.119776	\N
552	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:30:23.589344	\N
553	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:34:46.33156	\N
554	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:34:54.510041	\N
555	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:35:45.870642	\N
556	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:35:53.712204	\N
557	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:37:23.959558	\N
558	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:37:32.66496	\N
559	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:39:28.938805	\N
560	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:39:36.319456	\N
561	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:40:21.570817	\N
562	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:40:29.180039	\N
563	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:44:42.033825	\N
564	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:44:50.402802	\N
565	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:52:25.986092	\N
566	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:52:33.858621	\N
567	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:57:03.214701	\N
568	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 06:57:13.940966	\N
569	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 07:18:50.524106	\N
570	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-02 07:18:57.959747	\N
571	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-02 07:22:56.615791	\N
572	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 02:19:56.138407	\N
573	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 02:25:29.700048	\N
574	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 02:25:38.365998	\N
575	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 02:25:44.620485	\N
576	4	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 02:25:56.431865	\N
577	4	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 02:30:28.33995	\N
578	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 02:30:38.405495	\N
579	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "1", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.1.101	عبود	2026-09-04 03:12:44.799568	\N
580	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "2", "can_view": "True", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.1.101	عبود	2026-09-04 03:12:44.799568	\N
581	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "3", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.1.101	عبود	2026-09-04 03:12:44.799568	\N
582	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "4", "can_view": "True", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.1.101	عبود	2026-09-04 03:12:44.799568	\N
583	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "5", "can_view": "True", "can_add": "True", "can_edit": "True", "can_delete": "False", "can_print": "True", "can_cancel": "False"}	192.168.1.101	عبود	2026-09-04 03:12:44.799568	\N
584	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "6", "can_view": "True", "can_add": "True", "can_edit": "True", "can_delete": "False", "can_print": "True", "can_cancel": "False"}	192.168.1.101	عبود	2026-09-04 03:12:44.799568	\N
585	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "7", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.1.101	عبود	2026-09-04 03:12:44.799568	\N
586	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "8", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.1.101	عبود	2026-09-04 03:12:44.799568	\N
587	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "9", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.1.101	عبود	2026-09-04 03:12:44.799568	\N
588	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "10", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.1.101	عبود	2026-09-04 03:12:44.799568	\N
589	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "11", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.1.101	عبود	2026-09-04 03:12:44.799568	\N
590	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "12", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.1.101	عبود	2026-09-04 03:12:44.799568	\N
591	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "13", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.1.101	عبود	2026-09-04 03:12:44.799568	\N
592	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "14", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.1.101	عبود	2026-09-04 03:12:44.799568	\N
593	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "15", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.1.101	عبود	2026-09-04 03:12:44.799568	\N
594	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "16", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.1.101	عبود	2026-09-04 03:12:44.799568	\N
595	2	تسجيل الخروج	logout	\N	\N	\N	192.168.1.101	عبود	2026-09-04 03:12:48.468345	\N
596	2	تسجيل الدخول	login	\N	\N	\N	192.168.1.101	عبود	2026-09-04 03:12:56.087033	\N
597	2	تسجيل الخروج	logout	\N	\N	\N	192.168.1.101	عبود	2026-09-04 03:13:02.912201	\N
598	4	تسجيل الدخول	login	\N	\N	\N	192.168.1.101	عبود	2026-09-04 03:13:13.578752	\N
599	4	تسجيل الخروج	logout	\N	\N	\N	192.168.1.101	عبود	2026-09-04 03:17:01.917512	\N
600	2	تسجيل الدخول	login	\N	\N	\N	192.168.1.101	عبود	2026-09-04 03:17:11.349262	\N
601	2	تسجيل الخروج	logout	\N	\N	\N	192.168.1.101	عبود	2026-09-04 03:17:21.321326	\N
602	2	تسجيل الدخول	login	\N	\N	\N	192.168.1.101	عبود	2026-09-04 03:31:02.263937	\N
603	2	تسجيل الخروج	logout	\N	\N	\N	192.168.1.101	عبود	2026-09-04 03:40:44.088877	\N
604	4	تسجيل الدخول	login	\N	\N	\N	192.168.1.101	عبود	2026-09-04 03:40:57.878982	\N
605	4	تسجيل الخروج	logout	\N	\N	\N	192.168.1.101	عبود	2026-09-04 03:41:09.039576	\N
606	4	تسجيل الدخول	login	\N	\N	\N	10.13.84.133	عبود	2026-09-04 03:51:57.188479	\N
607	4	الطلاب	create	353	\N	"{Ellipsis}"	192.168.56.1	عبود	2026-09-04 03:54:37.896841	\N
608	4	الطلاب	delete	358	{"student_number": "ST-01-0358", "full_name": "آدم نوح"}	\N	192.168.56.1	عبود	2026-09-04 03:54:55.687171	\N
609	4	students	delete	358	{"id": "358", "student_number": "ST-01-0358", "full_name": "آدم نوح", "mother_name": "لينا", "gender": "ذكر", "nationality": "يمني", "status": "مستمر", "enrollment_type": "باقي", "student_status_reason": "None", "birth_date": "2008-09-19", "birth_village": "المنطقة", "birth_district": "الشرقية", "birth_governorate": "حضرموت", "transferred_from_school": "None", "transferred_district": "None", "transferred_governorate": "None", "transfer_date": "None", "academic_year_id": "1", "grade_id": "7", "section_id": "19", "parent_id": "40", "photo_url": "None", "created_at": "2026-08-24 22:59:44.680752", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-04 03:54:55.687171	\N
610	4	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 03:58:26.218649	\N
611	4	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 03:58:40.750491	\N
612	4	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 03:59:23.623954	\N
613	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 03:59:31.816883	\N
614	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 04:00:27.3639	\N
615	4	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 04:00:41.59616	\N
616	4	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 04:04:39.511106	\N
617	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 04:04:47.800716	\N
618	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 04:04:59.170365	\N
619	4	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 04:05:10.517747	\N
620	4	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 04:07:12.016888	\N
621	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 04:07:19.802713	\N
622	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "1", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:07:36.301379	\N
623	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "2", "can_view": "True", "can_add": "True", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:07:36.301379	\N
624	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "3", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:07:36.301379	\N
625	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "4", "can_view": "True", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:07:36.301379	\N
626	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "5", "can_view": "True", "can_add": "True", "can_edit": "True", "can_delete": "False", "can_print": "True", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:07:36.301379	\N
627	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "6", "can_view": "True", "can_add": "True", "can_edit": "True", "can_delete": "False", "can_print": "True", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:07:36.301379	\N
628	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "7", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:07:36.301379	\N
629	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "8", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:07:36.301379	\N
630	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "9", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:07:36.301379	\N
631	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "10", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:07:36.301379	\N
632	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "11", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:07:36.301379	\N
633	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "12", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:07:36.301379	\N
634	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "13", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:07:36.301379	\N
635	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "14", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:07:36.301379	\N
636	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "15", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:07:36.301379	\N
637	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "16", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:07:36.301379	\N
638	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 04:07:40.943742	\N
639	4	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 04:07:50.689449	\N
640	4	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 04:08:10.603173	\N
641	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 04:11:56.854316	\N
642	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "1", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:12:06.186341	\N
643	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "2", "can_view": "True", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:12:06.186341	\N
644	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "3", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:12:06.186341	\N
645	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "4", "can_view": "True", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:12:06.186341	\N
646	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "5", "can_view": "True", "can_add": "True", "can_edit": "True", "can_delete": "False", "can_print": "True", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:12:06.186341	\N
647	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "6", "can_view": "True", "can_add": "True", "can_edit": "True", "can_delete": "False", "can_print": "True", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:12:06.186341	\N
648	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "7", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:12:06.186341	\N
649	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "8", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:12:06.186341	\N
650	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "9", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:12:06.186341	\N
651	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "10", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:12:06.186341	\N
652	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "11", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:12:06.186341	\N
653	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "12", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:12:06.186341	\N
654	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "13", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:12:06.186341	\N
655	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "14", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:12:06.186341	\N
656	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "15", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:12:06.186341	\N
657	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "16", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 04:12:06.186341	\N
658	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 04:12:10.314799	\N
659	4	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 04:12:20.600268	\N
660	4	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 04:17:15.926987	\N
661	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 04:17:28.725453	\N
662	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 04:25:29.383205	\N
663	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 04:27:33.349997	\N
664	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 04:27:40.492241	\N
665	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 04:28:31.871334	\N
666	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 04:28:39.996818	\N
667	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 05:36:40.11578	\N
668	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 05:36:53.567202	\N
669	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 05:45:45.171323	\N
670	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 05:45:54.060967	\N
671	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 06:06:38.061778	\N
672	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 06:11:15.537636	\N
673	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 06:19:09.735072	\N
674	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "25", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
675	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "26", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
676	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "27", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
677	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "28", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
678	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "29", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
679	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "30", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
680	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "31", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
681	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "32", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
682	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "33", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
683	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "34", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
684	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "35", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
685	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "36", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
686	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "37", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
687	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "38", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
688	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "39", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
689	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "40", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
690	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "41", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
691	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "42", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
692	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "43", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
693	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "44", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
694	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "45", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
695	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "46", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
696	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "47", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
697	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "48", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
698	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "49", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
699	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "50", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
700	2	role_permissions	create	\N	\N	{"role_id": "6", "permission_id": "51", "can_view": "False", "can_add": "False", "can_edit": "False", "can_delete": "False", "can_print": "False", "can_cancel": "False"}	192.168.56.1	عبود	2026-09-04 06:19:28.59289	\N
701	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 06:20:15.045205	\N
702	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 06:20:42.29688	\N
703	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 06:27:54.384616	\N
704	4	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 06:28:08.879237	\N
705	4	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 06:28:38.374908	\N
706	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-04 06:30:02.592444	\N
707	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-04 08:05:58.979817	\N
708	2	تسجيل الدخول	login	\N	\N	\N	10.13.84.133	عبود	2026-09-04 08:49:05.559283	\N
709	2	تسجيل الخروج	logout	\N	\N	\N	10.13.84.133	عبود	2026-09-04 08:49:23.299013	\N
710	2	تسجيل الدخول	login	\N	\N	\N	10.13.84.133	عبود	2026-09-04 08:49:30.219129	\N
711	2	تسجيل الخروج	logout	\N	\N	\N	10.13.84.133	عبود	2026-09-04 08:49:34.102986	\N
712	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-05 01:09:34.215374	\N
713	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-05 01:22:53.490168	\N
714	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-05 01:23:10.590606	\N
715	2	subjects	create	11	\N	{"id": "11", "subject_name": "d", "min_pass_score": "50.0", "max_score": "100.0", "created_at": "2026-09-05 01:23:43.418637", "updated_at": "None"}	192.168.56.1	عبود	2026-09-05 01:23:43.418637	\N
716	2	subjects	delete	11	{"id": "11", "subject_name": "d", "min_pass_score": "50.00", "max_score": "100.00", "created_at": "2026-09-05 01:23:43.418637", "updated_at": "None"}	\N	192.168.56.1	عبود	2026-09-05 01:23:46.968338	\N
717	2	تسجيل الخروج	logout	\N	\N	\N	192.168.56.1	عبود	2026-09-05 01:51:38.84109	\N
718	2	تسجيل الدخول	login	\N	\N	\N	192.168.56.1	عبود	2026-09-05 01:51:55.971954	\N
\.


--
-- Data for Name: teacher_subject_sections; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.teacher_subject_sections (id, academic_year_id, grade_id, section_id, subject_id, teacher_id, created_at, updated_at) FROM stdin;
1	1	1	1	1	10	2026-08-24 22:59:44.680752	\N
2	1	1	1	2	24	2026-08-24 22:59:44.680752	\N
3	1	1	1	3	21	2026-08-24 22:59:44.680752	\N
4	1	1	1	4	26	2026-08-24 22:59:44.680752	\N
5	1	1	1	5	31	2026-08-24 22:59:44.680752	\N
6	1	1	2	1	5	2026-08-24 22:59:44.680752	\N
7	1	1	2	2	12	2026-08-24 22:59:44.680752	\N
8	1	1	2	3	5	2026-08-24 22:59:44.680752	\N
9	1	1	2	4	26	2026-08-24 22:59:44.680752	\N
10	1	1	2	5	26	2026-08-24 22:59:44.680752	\N
11	1	1	3	1	26	2026-08-24 22:59:44.680752	\N
12	1	1	3	2	24	2026-08-24 22:59:44.680752	\N
13	1	1	3	3	11	2026-08-24 22:59:44.680752	\N
14	1	1	3	4	18	2026-08-24 22:59:44.680752	\N
15	1	1	3	5	24	2026-08-24 22:59:44.680752	\N
16	1	2	4	1	29	2026-08-24 22:59:44.680752	\N
17	1	2	4	2	20	2026-08-24 22:59:44.680752	\N
18	1	2	4	3	11	2026-08-24 22:59:44.680752	\N
19	1	2	4	4	31	2026-08-24 22:59:44.680752	\N
20	1	2	4	5	20	2026-08-24 22:59:44.680752	\N
21	1	2	5	1	26	2026-08-24 22:59:44.680752	\N
22	1	2	5	2	26	2026-08-24 22:59:44.680752	\N
23	1	2	5	3	12	2026-08-24 22:59:44.680752	\N
24	1	2	5	4	10	2026-08-24 22:59:44.680752	\N
25	1	2	5	5	20	2026-08-24 22:59:44.680752	\N
26	1	2	6	1	18	2026-08-24 22:59:44.680752	\N
27	1	2	6	2	18	2026-08-24 22:59:44.680752	\N
28	1	2	6	3	10	2026-08-24 22:59:44.680752	\N
29	1	2	6	4	26	2026-08-24 22:59:44.680752	\N
30	1	2	6	5	11	2026-08-24 22:59:44.680752	\N
31	1	3	7	1	31	2026-08-24 22:59:44.680752	\N
32	1	3	7	2	18	2026-08-24 22:59:44.680752	\N
33	1	3	7	3	18	2026-08-24 22:59:44.680752	\N
34	1	3	7	4	21	2026-08-24 22:59:44.680752	\N
35	1	3	7	5	29	2026-08-24 22:59:44.680752	\N
36	1	3	8	1	11	2026-08-24 22:59:44.680752	\N
37	1	3	8	2	18	2026-08-24 22:59:44.680752	\N
38	1	3	8	3	24	2026-08-24 22:59:44.680752	\N
39	1	3	8	4	11	2026-08-24 22:59:44.680752	\N
40	1	3	8	5	29	2026-08-24 22:59:44.680752	\N
41	1	3	9	1	31	2026-08-24 22:59:44.680752	\N
42	1	3	9	2	5	2026-08-24 22:59:44.680752	\N
43	1	3	9	3	18	2026-08-24 22:59:44.680752	\N
44	1	3	9	4	18	2026-08-24 22:59:44.680752	\N
45	1	3	9	5	24	2026-08-24 22:59:44.680752	\N
46	1	4	10	1	26	2026-08-24 22:59:44.680752	\N
47	1	4	10	2	10	2026-08-24 22:59:44.680752	\N
48	1	4	10	3	24	2026-08-24 22:59:44.680752	\N
49	1	4	10	4	24	2026-08-24 22:59:44.680752	\N
50	1	4	10	5	10	2026-08-24 22:59:44.680752	\N
51	1	4	11	1	31	2026-08-24 22:59:44.680752	\N
52	1	4	11	2	11	2026-08-24 22:59:44.680752	\N
53	1	4	11	3	29	2026-08-24 22:59:44.680752	\N
54	1	4	11	4	12	2026-08-24 22:59:44.680752	\N
55	1	4	11	5	24	2026-08-24 22:59:44.680752	\N
56	1	4	12	1	26	2026-08-24 22:59:44.680752	\N
57	1	4	12	2	24	2026-08-24 22:59:44.680752	\N
58	1	4	12	3	5	2026-08-24 22:59:44.680752	\N
59	1	4	12	4	20	2026-08-24 22:59:44.680752	\N
60	1	4	12	5	30	2026-08-24 22:59:44.680752	\N
61	1	5	13	1	21	2026-08-24 22:59:44.680752	\N
62	1	5	13	2	10	2026-08-24 22:59:44.680752	\N
63	1	5	13	3	30	2026-08-24 22:59:44.680752	\N
64	1	5	13	4	30	2026-08-24 22:59:44.680752	\N
65	1	5	13	5	30	2026-08-24 22:59:44.680752	\N
66	1	5	14	1	18	2026-08-24 22:59:44.680752	\N
67	1	5	14	2	12	2026-08-24 22:59:44.680752	\N
68	1	5	14	3	30	2026-08-24 22:59:44.680752	\N
69	1	5	14	4	24	2026-08-24 22:59:44.680752	\N
70	1	5	14	5	26	2026-08-24 22:59:44.680752	\N
71	1	5	15	1	20	2026-08-24 22:59:44.680752	\N
72	1	5	15	2	30	2026-08-24 22:59:44.680752	\N
73	1	5	15	3	31	2026-08-24 22:59:44.680752	\N
74	1	5	15	4	21	2026-08-24 22:59:44.680752	\N
75	1	5	15	5	11	2026-08-24 22:59:44.680752	\N
76	1	6	16	1	31	2026-08-24 22:59:44.680752	\N
77	1	6	16	2	20	2026-08-24 22:59:44.680752	\N
78	1	6	16	3	11	2026-08-24 22:59:44.680752	\N
79	1	6	16	4	18	2026-08-24 22:59:44.680752	\N
80	1	6	16	5	5	2026-08-24 22:59:44.680752	\N
81	1	6	17	1	30	2026-08-24 22:59:44.680752	\N
82	1	6	17	2	18	2026-08-24 22:59:44.680752	\N
83	1	6	17	3	24	2026-08-24 22:59:44.680752	\N
84	1	6	17	4	5	2026-08-24 22:59:44.680752	\N
85	1	6	17	5	21	2026-08-24 22:59:44.680752	\N
86	1	6	18	1	24	2026-08-24 22:59:44.680752	\N
87	1	6	18	2	30	2026-08-24 22:59:44.680752	\N
88	1	6	18	3	31	2026-08-24 22:59:44.680752	\N
89	1	6	18	4	12	2026-08-24 22:59:44.680752	\N
90	1	6	18	5	26	2026-08-24 22:59:44.680752	\N
\.


--
-- Data for Name: term_exam_scores; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.term_exam_scores (id, student_id, academic_year_id, grade_id, section_id, subject_id, term, exam_score, created_at, updated_at) FROM stdin;
1	1	1	1	1	1	1	27.93	2026-08-24 22:59:44.680752	\N
2	1	1	1	1	2	1	12.55	2026-08-24 22:59:44.680752	\N
3	1	1	1	1	3	1	16.48	2026-08-24 22:59:44.680752	\N
4	1	1	1	1	4	1	25.28	2026-08-24 22:59:44.680752	\N
5	1	1	1	1	5	1	18.25	2026-08-24 22:59:44.680752	\N
6	2	1	1	1	1	1	18.17	2026-08-24 22:59:44.680752	\N
7	2	1	1	1	2	1	27.92	2026-08-24 22:59:44.680752	\N
8	2	1	1	1	3	1	8.87	2026-08-24 22:59:44.680752	\N
9	2	1	1	1	4	1	7.34	2026-08-24 22:59:44.680752	\N
10	2	1	1	1	5	1	19.44	2026-08-24 22:59:44.680752	\N
11	3	1	1	1	1	1	5.10	2026-08-24 22:59:44.680752	\N
12	3	1	1	1	2	1	9.26	2026-08-24 22:59:44.680752	\N
13	3	1	1	1	3	1	14.59	2026-08-24 22:59:44.680752	\N
14	3	1	1	1	4	1	7.07	2026-08-24 22:59:44.680752	\N
15	3	1	1	1	5	1	28.28	2026-08-24 22:59:44.680752	\N
16	4	1	1	1	1	1	14.85	2026-08-24 22:59:44.680752	\N
17	4	1	1	1	2	1	19.96	2026-08-24 22:59:44.680752	\N
18	4	1	1	1	3	1	10.75	2026-08-24 22:59:44.680752	\N
19	4	1	1	1	4	1	26.57	2026-08-24 22:59:44.680752	\N
20	4	1	1	1	5	1	5.31	2026-08-24 22:59:44.680752	\N
21	5	1	1	1	1	1	14.11	2026-08-24 22:59:44.680752	\N
22	5	1	1	1	2	1	27.85	2026-08-24 22:59:44.680752	\N
23	5	1	1	1	3	1	15.53	2026-08-24 22:59:44.680752	\N
24	5	1	1	1	4	1	7.28	2026-08-24 22:59:44.680752	\N
25	5	1	1	1	5	1	15.92	2026-08-24 22:59:44.680752	\N
26	6	1	1	1	1	1	20.25	2026-08-24 22:59:44.680752	\N
27	6	1	1	1	2	1	18.46	2026-08-24 22:59:44.680752	\N
28	6	1	1	1	3	1	13.17	2026-08-24 22:59:44.680752	\N
29	6	1	1	1	4	1	7.73	2026-08-24 22:59:44.680752	\N
30	6	1	1	1	5	1	15.99	2026-08-24 22:59:44.680752	\N
31	7	1	1	1	1	1	5.12	2026-08-24 22:59:44.680752	\N
32	7	1	1	1	2	1	20.56	2026-08-24 22:59:44.680752	\N
33	7	1	1	1	3	1	15.90	2026-08-24 22:59:44.680752	\N
34	7	1	1	1	4	1	15.13	2026-08-24 22:59:44.680752	\N
35	7	1	1	1	5	1	29.48	2026-08-24 22:59:44.680752	\N
36	8	1	1	1	1	1	18.80	2026-08-24 22:59:44.680752	\N
37	8	1	1	1	2	1	29.41	2026-08-24 22:59:44.680752	\N
38	8	1	1	1	3	1	27.25	2026-08-24 22:59:44.680752	\N
39	8	1	1	1	4	1	27.48	2026-08-24 22:59:44.680752	\N
40	8	1	1	1	5	1	23.90	2026-08-24 22:59:44.680752	\N
41	9	1	1	1	1	1	16.75	2026-08-24 22:59:44.680752	\N
42	9	1	1	1	2	1	10.66	2026-08-24 22:59:44.680752	\N
43	9	1	1	1	3	1	25.71	2026-08-24 22:59:44.680752	\N
44	9	1	1	1	4	1	13.06	2026-08-24 22:59:44.680752	\N
45	9	1	1	1	5	1	20.37	2026-08-24 22:59:44.680752	\N
46	10	1	1	1	1	1	25.95	2026-08-24 22:59:44.680752	\N
47	10	1	1	1	2	1	26.74	2026-08-24 22:59:44.680752	\N
48	10	1	1	1	3	1	27.93	2026-08-24 22:59:44.680752	\N
49	10	1	1	1	4	1	29.83	2026-08-24 22:59:44.680752	\N
50	10	1	1	1	5	1	15.48	2026-08-24 22:59:44.680752	\N
51	11	1	1	1	1	1	25.32	2026-08-24 22:59:44.680752	\N
52	11	1	1	1	2	1	11.86	2026-08-24 22:59:44.680752	\N
53	11	1	1	1	3	1	20.44	2026-08-24 22:59:44.680752	\N
54	11	1	1	1	4	1	24.65	2026-08-24 22:59:44.680752	\N
55	11	1	1	1	5	1	29.15	2026-08-24 22:59:44.680752	\N
56	12	1	1	1	1	1	7.94	2026-08-24 22:59:44.680752	\N
57	12	1	1	1	2	1	21.52	2026-08-24 22:59:44.680752	\N
58	12	1	1	1	3	1	12.52	2026-08-24 22:59:44.680752	\N
59	12	1	1	1	4	1	26.33	2026-08-24 22:59:44.680752	\N
60	12	1	1	1	5	1	14.33	2026-08-24 22:59:44.680752	\N
61	13	1	1	1	1	1	8.38	2026-08-24 22:59:44.680752	\N
62	13	1	1	1	2	1	19.72	2026-08-24 22:59:44.680752	\N
63	13	1	1	1	3	1	22.43	2026-08-24 22:59:44.680752	\N
64	13	1	1	1	4	1	21.32	2026-08-24 22:59:44.680752	\N
65	13	1	1	1	5	1	6.58	2026-08-24 22:59:44.680752	\N
66	14	1	1	1	1	1	11.53	2026-08-24 22:59:44.680752	\N
67	14	1	1	1	2	1	7.69	2026-08-24 22:59:44.680752	\N
68	14	1	1	1	3	1	27.33	2026-08-24 22:59:44.680752	\N
69	14	1	1	1	4	1	17.89	2026-08-24 22:59:44.680752	\N
70	14	1	1	1	5	1	14.73	2026-08-24 22:59:44.680752	\N
71	15	1	1	1	1	1	19.11	2026-08-24 22:59:44.680752	\N
72	15	1	1	1	2	1	18.28	2026-08-24 22:59:44.680752	\N
73	15	1	1	1	3	1	15.59	2026-08-24 22:59:44.680752	\N
74	15	1	1	1	4	1	20.09	2026-08-24 22:59:44.680752	\N
75	15	1	1	1	5	1	18.36	2026-08-24 22:59:44.680752	\N
76	16	1	1	1	1	1	12.44	2026-08-24 22:59:44.680752	\N
77	16	1	1	1	2	1	8.44	2026-08-24 22:59:44.680752	\N
78	16	1	1	1	3	1	10.42	2026-08-24 22:59:44.680752	\N
79	16	1	1	1	4	1	13.75	2026-08-24 22:59:44.680752	\N
80	16	1	1	1	5	1	25.21	2026-08-24 22:59:44.680752	\N
81	17	1	1	1	1	1	5.07	2026-08-24 22:59:44.680752	\N
82	17	1	1	1	2	1	27.06	2026-08-24 22:59:44.680752	\N
83	17	1	1	1	3	1	18.30	2026-08-24 22:59:44.680752	\N
84	17	1	1	1	4	1	23.39	2026-08-24 22:59:44.680752	\N
85	17	1	1	1	5	1	15.62	2026-08-24 22:59:44.680752	\N
87	18	1	1	1	2	1	6.63	2026-08-24 22:59:44.680752	\N
88	18	1	1	1	3	1	8.07	2026-08-24 22:59:44.680752	\N
89	18	1	1	1	4	1	22.54	2026-08-24 22:59:44.680752	\N
90	18	1	1	1	5	1	14.50	2026-08-24 22:59:44.680752	\N
91	19	1	1	1	1	1	28.50	2026-08-24 22:59:44.680752	\N
92	19	1	1	1	2	1	23.46	2026-08-24 22:59:44.680752	\N
93	19	1	1	1	3	1	18.63	2026-08-24 22:59:44.680752	\N
94	19	1	1	1	4	1	10.07	2026-08-24 22:59:44.680752	\N
95	19	1	1	1	5	1	20.76	2026-08-24 22:59:44.680752	\N
96	20	1	1	2	1	1	12.73	2026-08-24 22:59:44.680752	\N
97	20	1	1	2	2	1	27.98	2026-08-24 22:59:44.680752	\N
98	20	1	1	2	3	1	14.29	2026-08-24 22:59:44.680752	\N
99	20	1	1	2	4	1	16.54	2026-08-24 22:59:44.680752	\N
100	20	1	1	2	5	1	18.17	2026-08-24 22:59:44.680752	\N
101	21	1	1	2	1	1	23.91	2026-08-24 22:59:44.680752	\N
102	21	1	1	2	2	1	14.11	2026-08-24 22:59:44.680752	\N
103	21	1	1	2	3	1	14.99	2026-08-24 22:59:44.680752	\N
104	21	1	1	2	4	1	9.73	2026-08-24 22:59:44.680752	\N
105	21	1	1	2	5	1	19.04	2026-08-24 22:59:44.680752	\N
106	22	1	1	2	1	1	25.22	2026-08-24 22:59:44.680752	\N
107	22	1	1	2	2	1	8.77	2026-08-24 22:59:44.680752	\N
108	22	1	1	2	3	1	6.64	2026-08-24 22:59:44.680752	\N
109	22	1	1	2	4	1	11.34	2026-08-24 22:59:44.680752	\N
110	22	1	1	2	5	1	9.57	2026-08-24 22:59:44.680752	\N
111	23	1	1	2	1	1	16.13	2026-08-24 22:59:44.680752	\N
112	23	1	1	2	2	1	29.78	2026-08-24 22:59:44.680752	\N
113	23	1	1	2	3	1	25.54	2026-08-24 22:59:44.680752	\N
114	23	1	1	2	4	1	14.88	2026-08-24 22:59:44.680752	\N
115	23	1	1	2	5	1	29.60	2026-08-24 22:59:44.680752	\N
116	24	1	1	2	1	1	6.06	2026-08-24 22:59:44.680752	\N
117	24	1	1	2	2	1	14.76	2026-08-24 22:59:44.680752	\N
118	24	1	1	2	3	1	11.19	2026-08-24 22:59:44.680752	\N
119	24	1	1	2	4	1	6.76	2026-08-24 22:59:44.680752	\N
120	24	1	1	2	5	1	18.19	2026-08-24 22:59:44.680752	\N
121	25	1	1	2	1	1	20.56	2026-08-24 22:59:44.680752	\N
122	25	1	1	2	2	1	26.58	2026-08-24 22:59:44.680752	\N
123	25	1	1	2	3	1	26.37	2026-08-24 22:59:44.680752	\N
124	25	1	1	2	4	1	28.41	2026-08-24 22:59:44.680752	\N
125	25	1	1	2	5	1	5.31	2026-08-24 22:59:44.680752	\N
126	26	1	1	2	1	1	21.03	2026-08-24 22:59:44.680752	\N
127	26	1	1	2	2	1	7.98	2026-08-24 22:59:44.680752	\N
128	26	1	1	2	3	1	18.33	2026-08-24 22:59:44.680752	\N
129	26	1	1	2	4	1	21.20	2026-08-24 22:59:44.680752	\N
130	26	1	1	2	5	1	19.97	2026-08-24 22:59:44.680752	\N
131	27	1	1	2	1	1	23.78	2026-08-24 22:59:44.680752	\N
132	27	1	1	2	2	1	14.64	2026-08-24 22:59:44.680752	\N
133	27	1	1	2	3	1	5.22	2026-08-24 22:59:44.680752	\N
134	27	1	1	2	4	1	5.93	2026-08-24 22:59:44.680752	\N
135	27	1	1	2	5	1	20.02	2026-08-24 22:59:44.680752	\N
136	28	1	1	2	1	1	6.87	2026-08-24 22:59:44.680752	\N
137	28	1	1	2	2	1	10.09	2026-08-24 22:59:44.680752	\N
138	28	1	1	2	3	1	9.66	2026-08-24 22:59:44.680752	\N
139	28	1	1	2	4	1	7.26	2026-08-24 22:59:44.680752	\N
140	28	1	1	2	5	1	16.95	2026-08-24 22:59:44.680752	\N
141	29	1	1	2	1	1	27.33	2026-08-24 22:59:44.680752	\N
142	29	1	1	2	2	1	12.77	2026-08-24 22:59:44.680752	\N
143	29	1	1	2	3	1	8.06	2026-08-24 22:59:44.680752	\N
144	29	1	1	2	4	1	6.43	2026-08-24 22:59:44.680752	\N
145	29	1	1	2	5	1	17.66	2026-08-24 22:59:44.680752	\N
146	30	1	1	2	1	1	28.09	2026-08-24 22:59:44.680752	\N
147	30	1	1	2	2	1	28.40	2026-08-24 22:59:44.680752	\N
148	30	1	1	2	3	1	24.70	2026-08-24 22:59:44.680752	\N
149	30	1	1	2	4	1	15.88	2026-08-24 22:59:44.680752	\N
150	30	1	1	2	5	1	11.07	2026-08-24 22:59:44.680752	\N
151	31	1	1	2	1	1	17.54	2026-08-24 22:59:44.680752	\N
152	31	1	1	2	2	1	10.67	2026-08-24 22:59:44.680752	\N
153	31	1	1	2	3	1	8.70	2026-08-24 22:59:44.680752	\N
154	31	1	1	2	4	1	21.65	2026-08-24 22:59:44.680752	\N
155	31	1	1	2	5	1	8.00	2026-08-24 22:59:44.680752	\N
156	32	1	1	2	1	1	26.94	2026-08-24 22:59:44.680752	\N
157	32	1	1	2	2	1	22.73	2026-08-24 22:59:44.680752	\N
158	32	1	1	2	3	1	5.40	2026-08-24 22:59:44.680752	\N
159	32	1	1	2	4	1	25.30	2026-08-24 22:59:44.680752	\N
160	32	1	1	2	5	1	6.75	2026-08-24 22:59:44.680752	\N
161	33	1	1	2	1	1	6.45	2026-08-24 22:59:44.680752	\N
162	33	1	1	2	2	1	20.36	2026-08-24 22:59:44.680752	\N
163	33	1	1	2	3	1	29.21	2026-08-24 22:59:44.680752	\N
164	33	1	1	2	4	1	12.31	2026-08-24 22:59:44.680752	\N
165	33	1	1	2	5	1	22.55	2026-08-24 22:59:44.680752	\N
166	34	1	1	2	1	1	5.87	2026-08-24 22:59:44.680752	\N
167	34	1	1	2	2	1	12.84	2026-08-24 22:59:44.680752	\N
168	34	1	1	2	3	1	29.28	2026-08-24 22:59:44.680752	\N
169	34	1	1	2	4	1	6.41	2026-08-24 22:59:44.680752	\N
170	34	1	1	2	5	1	8.86	2026-08-24 22:59:44.680752	\N
171	35	1	1	3	1	1	12.97	2026-08-24 22:59:44.680752	\N
172	35	1	1	3	2	1	21.15	2026-08-24 22:59:44.680752	\N
173	35	1	1	3	3	1	23.39	2026-08-24 22:59:44.680752	\N
174	35	1	1	3	4	1	24.07	2026-08-24 22:59:44.680752	\N
175	35	1	1	3	5	1	28.67	2026-08-24 22:59:44.680752	\N
176	36	1	1	3	1	1	17.54	2026-08-24 22:59:44.680752	\N
177	36	1	1	3	2	1	7.18	2026-08-24 22:59:44.680752	\N
178	36	1	1	3	3	1	14.43	2026-08-24 22:59:44.680752	\N
179	36	1	1	3	4	1	10.16	2026-08-24 22:59:44.680752	\N
180	36	1	1	3	5	1	23.82	2026-08-24 22:59:44.680752	\N
181	37	1	1	3	1	1	6.87	2026-08-24 22:59:44.680752	\N
182	37	1	1	3	2	1	19.65	2026-08-24 22:59:44.680752	\N
183	37	1	1	3	3	1	12.31	2026-08-24 22:59:44.680752	\N
184	37	1	1	3	4	1	23.11	2026-08-24 22:59:44.680752	\N
185	37	1	1	3	5	1	9.61	2026-08-24 22:59:44.680752	\N
186	38	1	1	3	1	1	19.60	2026-08-24 22:59:44.680752	\N
187	38	1	1	3	2	1	29.45	2026-08-24 22:59:44.680752	\N
188	38	1	1	3	3	1	7.13	2026-08-24 22:59:44.680752	\N
189	38	1	1	3	4	1	15.99	2026-08-24 22:59:44.680752	\N
190	38	1	1	3	5	1	26.87	2026-08-24 22:59:44.680752	\N
191	39	1	1	3	1	1	8.24	2026-08-24 22:59:44.680752	\N
192	39	1	1	3	2	1	16.71	2026-08-24 22:59:44.680752	\N
193	39	1	1	3	3	1	15.71	2026-08-24 22:59:44.680752	\N
194	39	1	1	3	4	1	7.48	2026-08-24 22:59:44.680752	\N
195	39	1	1	3	5	1	20.26	2026-08-24 22:59:44.680752	\N
196	40	1	1	3	1	1	20.63	2026-08-24 22:59:44.680752	\N
197	40	1	1	3	2	1	28.82	2026-08-24 22:59:44.680752	\N
198	40	1	1	3	3	1	14.76	2026-08-24 22:59:44.680752	\N
199	40	1	1	3	4	1	17.02	2026-08-24 22:59:44.680752	\N
200	40	1	1	3	5	1	22.47	2026-08-24 22:59:44.680752	\N
86	18	1	1	1	1	1	22.73	2026-08-24 22:59:44.680752	2026-09-02 04:14:16.650216
201	693	1	1	1	1	1	8.00	2026-09-02 04:14:05.053421	2026-09-02 04:14:16.650216
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, employee_id, username, password_hash, role_id, profile_image, phone, email, status, last_login, last_password_change, created_at, updated_at) FROM stdin;
1	1	admin	19e88a9d839a5de0f26a3b82ebade95d$fc3167cc5fb4e6edaa686d5e424920a30717d95ae447efd3c5e34bcb74a23736	1	\N	\N	\N	موقف	2026-08-21 02:19:10.710825	\N	2026-08-21 02:18:55.612715	2026-08-30 03:04:43.316627
3	\N	aa	174beaf4c78b585d93d7d2c44ec6a8eb$5cb22df5af6058f6503b8c393a3d6a5e8babaae8f3bbd23fbfcc201765583630	6	\N	\N	\N	نشط	2026-08-21 03:49:56.20009	\N	2026-08-21 03:49:32.936059	2026-08-21 03:49:56.127817
4	11	aaa	7ed3991fe477c79420ed945f40a8c1e1$72184359e9a7b49da2a54bed8dca6b4008ea707eff0d1b5d532b92ec953a8efa	6	\N	\N	\N	نشط	2026-09-04 06:28:08.364753	\N	2026-08-30 17:37:47.774945	2026-09-04 06:28:08.322855
2	1	a	44ff60c07d7093877af0235976031194$89c210f37100c53dcffa4d3f93df3af007d38af3d462f46e14a7e0f9dc2fe0dc	1	\N	\N	\N	نشط	2026-09-05 01:51:55.418293	\N	2026-08-21 02:19:42.406058	2026-09-05 04:14:45.812069
\.


--
-- Data for Name: weekly_schedules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.weekly_schedules (id, academic_year_id, term, grade_id, section_id, day_of_week, period_number, subject_id, teacher_id, created_at, updated_at) FROM stdin;
13	1	1	1	1	saturday	1	1	\N	2026-09-02 04:32:05.434719	\N
14	1	1	1	1	monday	1	5	\N	2026-09-02 04:32:05.434719	\N
15	1	2	1	1	saturday	1	1	\N	2026-09-02 04:32:47.453395	\N
16	1	2	1	1	sunday	1	5	\N	2026-09-02 04:32:47.453395	\N
17	1	2	1	1	monday	1	4	\N	2026-09-02 04:32:47.453395	\N
18	1	2	1	1	tuesday	1	2	\N	2026-09-02 04:32:47.453395	\N
\.


--
-- Name: academic_years_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.academic_years_id_seq', 2, true);


--
-- Name: annual_closing_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.annual_closing_logs_id_seq', 1, false);


--
-- Name: backup_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.backup_logs_id_seq', 1, false);


--
-- Name: behavioral_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.behavioral_records_id_seq', 55, true);


--
-- Name: daily_attendance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.daily_attendance_id_seq', 1712, true);


--
-- Name: employee_allowances_deductions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.employee_allowances_deductions_id_seq', 29, true);


--
-- Name: employee_loans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.employee_loans_id_seq', 9, true);


--
-- Name: employees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.employees_id_seq', 94, true);


--
-- Name: expense_vouchers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.expense_vouchers_id_seq', 40, true);


--
-- Name: fee_installments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fee_installments_id_seq', 277, true);


--
-- Name: fee_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fee_types_id_seq', 6, true);


--
-- Name: final_exam_schedules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.final_exam_schedules_id_seq', 1, false);


--
-- Name: grade_fee_structures_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.grade_fee_structures_id_seq', 75, true);


--
-- Name: grades_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.grades_id_seq', 15, true);


--
-- Name: homeworks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.homeworks_id_seq', 38, true);


--
-- Name: import_export_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.import_export_logs_id_seq', 1, false);


--
-- Name: monthly_evaluations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.monthly_evaluations_id_seq', 619, true);


--
-- Name: monthly_exam_schedules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.monthly_exam_schedules_id_seq', 15, true);


--
-- Name: notification_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notification_logs_id_seq', 300, true);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notifications_id_seq', 8, true);


--
-- Name: parent_devices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.parent_devices_id_seq', 1, false);


--
-- Name: parents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.parents_id_seq', 294, true);


--
-- Name: payroll_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payroll_records_id_seq', 115, true);


--
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.permissions_id_seq', 105, true);


--
-- Name: print_archive_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.print_archive_id_seq', 1, false);


--
-- Name: receipts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.receipts_id_seq', 120, true);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 7, true);


--
-- Name: school_info_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.school_info_id_seq', 1, true);


--
-- Name: sections_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sections_id_seq', 71, true);


--
-- Name: student_academic_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_academic_history_id_seq', 1, false);


--
-- Name: student_documents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_documents_id_seq', 1, true);


--
-- Name: student_fees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_fees_id_seq', 80, true);


--
-- Name: students_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.students_id_seq', 695, true);


--
-- Name: subjects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.subjects_id_seq', 11, true);


--
-- Name: system_audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.system_audit_logs_id_seq', 718, true);


--
-- Name: teacher_subject_sections_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.teacher_subject_sections_id_seq', 90, true);


--
-- Name: term_exam_scores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.term_exam_scores_id_seq', 201, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 4, true);


--
-- Name: weekly_schedules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.weekly_schedules_id_seq', 18, true);


--
-- Name: academic_years academic_years_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.academic_years
    ADD CONSTRAINT academic_years_pkey PRIMARY KEY (id);


--
-- Name: annual_closing_logs annual_closing_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annual_closing_logs
    ADD CONSTRAINT annual_closing_logs_pkey PRIMARY KEY (id);


--
-- Name: backup_logs backup_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.backup_logs
    ADD CONSTRAINT backup_logs_pkey PRIMARY KEY (id);


--
-- Name: behavioral_records behavioral_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.behavioral_records
    ADD CONSTRAINT behavioral_records_pkey PRIMARY KEY (id);


--
-- Name: daily_attendance daily_attendance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_attendance
    ADD CONSTRAINT daily_attendance_pkey PRIMARY KEY (id);


--
-- Name: employee_allowances_deductions employee_allowances_deductions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_allowances_deductions
    ADD CONSTRAINT employee_allowances_deductions_pkey PRIMARY KEY (id);


--
-- Name: employee_loans employee_loans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_loans
    ADD CONSTRAINT employee_loans_pkey PRIMARY KEY (id);


--
-- Name: employees employees_national_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_national_id_key UNIQUE (national_id);


--
-- Name: employees employees_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_pkey PRIMARY KEY (id);


--
-- Name: expense_vouchers expense_vouchers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_vouchers
    ADD CONSTRAINT expense_vouchers_pkey PRIMARY KEY (id);


--
-- Name: expense_vouchers expense_vouchers_voucher_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_vouchers
    ADD CONSTRAINT expense_vouchers_voucher_number_key UNIQUE (voucher_number);


--
-- Name: fee_installments fee_installments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fee_installments
    ADD CONSTRAINT fee_installments_pkey PRIMARY KEY (id);


--
-- Name: fee_types fee_types_fee_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fee_types
    ADD CONSTRAINT fee_types_fee_name_key UNIQUE (fee_name);


--
-- Name: fee_types fee_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fee_types
    ADD CONSTRAINT fee_types_pkey PRIMARY KEY (id);


--
-- Name: final_exam_schedules final_exam_schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.final_exam_schedules
    ADD CONSTRAINT final_exam_schedules_pkey PRIMARY KEY (id);


--
-- Name: grade_fee_structures grade_fee_structures_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grade_fee_structures
    ADD CONSTRAINT grade_fee_structures_pkey PRIMARY KEY (id);


--
-- Name: grades grades_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grades
    ADD CONSTRAINT grades_pkey PRIMARY KEY (id);


--
-- Name: homeworks homeworks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.homeworks
    ADD CONSTRAINT homeworks_pkey PRIMARY KEY (id);


--
-- Name: import_export_logs import_export_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.import_export_logs
    ADD CONSTRAINT import_export_logs_pkey PRIMARY KEY (id);


--
-- Name: monthly_evaluations monthly_evaluations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monthly_evaluations
    ADD CONSTRAINT monthly_evaluations_pkey PRIMARY KEY (id);


--
-- Name: monthly_exam_schedules monthly_exam_schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monthly_exam_schedules
    ADD CONSTRAINT monthly_exam_schedules_pkey PRIMARY KEY (id);


--
-- Name: notification_logs notification_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_logs
    ADD CONSTRAINT notification_logs_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: parent_devices parent_devices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parent_devices
    ADD CONSTRAINT parent_devices_pkey PRIMARY KEY (id);


--
-- Name: parents parents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parents
    ADD CONSTRAINT parents_pkey PRIMARY KEY (id);


--
-- Name: parents parents_primary_phone_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parents
    ADD CONSTRAINT parents_primary_phone_key UNIQUE (primary_phone);


--
-- Name: payroll_records payroll_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payroll_records
    ADD CONSTRAINT payroll_records_pkey PRIMARY KEY (id);


--
-- Name: permissions permissions_permission_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_permission_key_key UNIQUE (permission_key);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: print_archive print_archive_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.print_archive
    ADD CONSTRAINT print_archive_pkey PRIMARY KEY (id);


--
-- Name: receipts receipts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.receipts
    ADD CONSTRAINT receipts_pkey PRIMARY KEY (id);


--
-- Name: receipts receipts_receipt_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.receipts
    ADD CONSTRAINT receipts_receipt_number_key UNIQUE (receipt_number);


--
-- Name: role_permissions role_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_pkey PRIMARY KEY (role_id, permission_id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: roles roles_role_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_role_name_key UNIQUE (role_name);


--
-- Name: school_info school_info_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.school_info
    ADD CONSTRAINT school_info_pkey PRIMARY KEY (id);


--
-- Name: sections sections_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT sections_pkey PRIMARY KEY (id);


--
-- Name: student_academic_history student_academic_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_academic_history
    ADD CONSTRAINT student_academic_history_pkey PRIMARY KEY (id);


--
-- Name: student_documents student_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_documents
    ADD CONSTRAINT student_documents_pkey PRIMARY KEY (id);


--
-- Name: student_fees student_fees_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_fees
    ADD CONSTRAINT student_fees_pkey PRIMARY KEY (id);


--
-- Name: students students_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (id);


--
-- Name: students students_student_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_student_number_key UNIQUE (student_number);


--
-- Name: subjects subjects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subjects
    ADD CONSTRAINT subjects_pkey PRIMARY KEY (id);


--
-- Name: system_audit_logs system_audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_audit_logs
    ADD CONSTRAINT system_audit_logs_pkey PRIMARY KEY (id);


--
-- Name: teacher_subject_sections teacher_subject_sections_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_subject_sections
    ADD CONSTRAINT teacher_subject_sections_pkey PRIMARY KEY (id);


--
-- Name: term_exam_scores term_exam_scores_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.term_exam_scores
    ADD CONSTRAINT term_exam_scores_pkey PRIMARY KEY (id);


--
-- Name: payroll_records uq_employee_monthly_payroll; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payroll_records
    ADD CONSTRAINT uq_employee_monthly_payroll UNIQUE (employee_id, month, year);


--
-- Name: grade_fee_structures uq_grade_fee; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grade_fee_structures
    ADD CONSTRAINT uq_grade_fee UNIQUE (academic_year_id, grade_id, fee_type_id);


--
-- Name: sections uq_grade_section; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT uq_grade_section UNIQUE (grade_id, section_name);


--
-- Name: weekly_schedules uq_schedule_slot; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weekly_schedules
    ADD CONSTRAINT uq_schedule_slot UNIQUE (academic_year_id, term, section_id, day_of_week, period_number);


--
-- Name: daily_attendance uq_student_daily_attendance; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_attendance
    ADD CONSTRAINT uq_student_daily_attendance UNIQUE (student_id, attendance_date);


--
-- Name: monthly_evaluations uq_student_monthly_eval; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monthly_evaluations
    ADD CONSTRAINT uq_student_monthly_eval UNIQUE (student_id, academic_year_id, subject_id, term, month);


--
-- Name: term_exam_scores uq_student_term_exam; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.term_exam_scores
    ADD CONSTRAINT uq_student_term_exam UNIQUE (student_id, academic_year_id, subject_id, term);


--
-- Name: student_fees uq_student_year_fee; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_fees
    ADD CONSTRAINT uq_student_year_fee UNIQUE (student_id, academic_year_id);


--
-- Name: student_academic_history uq_student_year_history; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_academic_history
    ADD CONSTRAINT uq_student_year_history UNIQUE (student_id, academic_year_id);


--
-- Name: teacher_subject_sections uq_teacher_assignment; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_subject_sections
    ADD CONSTRAINT uq_teacher_assignment UNIQUE (academic_year_id, section_id, subject_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: weekly_schedules weekly_schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weekly_schedules
    ADD CONSTRAINT weekly_schedules_pkey PRIMARY KEY (id);


--
-- Name: academic_years academic_years_closed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.academic_years
    ADD CONSTRAINT academic_years_closed_by_user_id_fkey FOREIGN KEY (closed_by_user_id) REFERENCES public.users(id);


--
-- Name: annual_closing_logs annual_closing_logs_executed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annual_closing_logs
    ADD CONSTRAINT annual_closing_logs_executed_by_user_id_fkey FOREIGN KEY (executed_by_user_id) REFERENCES public.users(id);


--
-- Name: annual_closing_logs annual_closing_logs_from_academic_year_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annual_closing_logs
    ADD CONSTRAINT annual_closing_logs_from_academic_year_id_fkey FOREIGN KEY (from_academic_year_id) REFERENCES public.academic_years(id);


--
-- Name: annual_closing_logs annual_closing_logs_to_academic_year_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.annual_closing_logs
    ADD CONSTRAINT annual_closing_logs_to_academic_year_id_fkey FOREIGN KEY (to_academic_year_id) REFERENCES public.academic_years(id);


--
-- Name: backup_logs backup_logs_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.backup_logs
    ADD CONSTRAINT backup_logs_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id);


--
-- Name: behavioral_records behavioral_records_academic_year_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.behavioral_records
    ADD CONSTRAINT behavioral_records_academic_year_id_fkey FOREIGN KEY (academic_year_id) REFERENCES public.academic_years(id);


--
-- Name: behavioral_records behavioral_records_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.behavioral_records
    ADD CONSTRAINT behavioral_records_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- Name: daily_attendance daily_attendance_academic_year_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_attendance
    ADD CONSTRAINT daily_attendance_academic_year_id_fkey FOREIGN KEY (academic_year_id) REFERENCES public.academic_years(id);


--
-- Name: daily_attendance daily_attendance_grade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_attendance
    ADD CONSTRAINT daily_attendance_grade_id_fkey FOREIGN KEY (grade_id) REFERENCES public.grades(id);


--
-- Name: daily_attendance daily_attendance_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_attendance
    ADD CONSTRAINT daily_attendance_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id);


--
-- Name: daily_attendance daily_attendance_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_attendance
    ADD CONSTRAINT daily_attendance_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- Name: employee_allowances_deductions employee_allowances_deductions_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_allowances_deductions
    ADD CONSTRAINT employee_allowances_deductions_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE CASCADE;


--
-- Name: employee_loans employee_loans_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_loans
    ADD CONSTRAINT employee_loans_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE CASCADE;


--
-- Name: expense_vouchers expense_vouchers_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expense_vouchers
    ADD CONSTRAINT expense_vouchers_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id);


--
-- Name: fee_installments fee_installments_student_fee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fee_installments
    ADD CONSTRAINT fee_installments_student_fee_id_fkey FOREIGN KEY (student_fee_id) REFERENCES public.student_fees(id) ON DELETE CASCADE;


--
-- Name: final_exam_schedules final_exam_schedules_academic_year_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.final_exam_schedules
    ADD CONSTRAINT final_exam_schedules_academic_year_id_fkey FOREIGN KEY (academic_year_id) REFERENCES public.academic_years(id);


--
-- Name: final_exam_schedules final_exam_schedules_grade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.final_exam_schedules
    ADD CONSTRAINT final_exam_schedules_grade_id_fkey FOREIGN KEY (grade_id) REFERENCES public.grades(id);


--
-- Name: final_exam_schedules final_exam_schedules_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.final_exam_schedules
    ADD CONSTRAINT final_exam_schedules_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id);


--
-- Name: grade_fee_structures grade_fee_structures_academic_year_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grade_fee_structures
    ADD CONSTRAINT grade_fee_structures_academic_year_id_fkey FOREIGN KEY (academic_year_id) REFERENCES public.academic_years(id) ON DELETE CASCADE;


--
-- Name: grade_fee_structures grade_fee_structures_fee_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grade_fee_structures
    ADD CONSTRAINT grade_fee_structures_fee_type_id_fkey FOREIGN KEY (fee_type_id) REFERENCES public.fee_types(id) ON DELETE CASCADE;


--
-- Name: grade_fee_structures grade_fee_structures_grade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grade_fee_structures
    ADD CONSTRAINT grade_fee_structures_grade_id_fkey FOREIGN KEY (grade_id) REFERENCES public.grades(id) ON DELETE CASCADE;


--
-- Name: homeworks homeworks_academic_year_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.homeworks
    ADD CONSTRAINT homeworks_academic_year_id_fkey FOREIGN KEY (academic_year_id) REFERENCES public.academic_years(id);


--
-- Name: homeworks homeworks_grade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.homeworks
    ADD CONSTRAINT homeworks_grade_id_fkey FOREIGN KEY (grade_id) REFERENCES public.grades(id);


--
-- Name: homeworks homeworks_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.homeworks
    ADD CONSTRAINT homeworks_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id);


--
-- Name: homeworks homeworks_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.homeworks
    ADD CONSTRAINT homeworks_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id);


--
-- Name: import_export_logs import_export_logs_executed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.import_export_logs
    ADD CONSTRAINT import_export_logs_executed_by_fkey FOREIGN KEY (executed_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: monthly_evaluations monthly_evaluations_academic_year_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monthly_evaluations
    ADD CONSTRAINT monthly_evaluations_academic_year_id_fkey FOREIGN KEY (academic_year_id) REFERENCES public.academic_years(id);


--
-- Name: monthly_evaluations monthly_evaluations_grade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monthly_evaluations
    ADD CONSTRAINT monthly_evaluations_grade_id_fkey FOREIGN KEY (grade_id) REFERENCES public.grades(id);


--
-- Name: monthly_evaluations monthly_evaluations_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monthly_evaluations
    ADD CONSTRAINT monthly_evaluations_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id);


--
-- Name: monthly_evaluations monthly_evaluations_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monthly_evaluations
    ADD CONSTRAINT monthly_evaluations_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- Name: monthly_evaluations monthly_evaluations_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monthly_evaluations
    ADD CONSTRAINT monthly_evaluations_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id);


--
-- Name: monthly_exam_schedules monthly_exam_schedules_academic_year_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monthly_exam_schedules
    ADD CONSTRAINT monthly_exam_schedules_academic_year_id_fkey FOREIGN KEY (academic_year_id) REFERENCES public.academic_years(id);


--
-- Name: monthly_exam_schedules monthly_exam_schedules_grade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monthly_exam_schedules
    ADD CONSTRAINT monthly_exam_schedules_grade_id_fkey FOREIGN KEY (grade_id) REFERENCES public.grades(id);


--
-- Name: monthly_exam_schedules monthly_exam_schedules_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monthly_exam_schedules
    ADD CONSTRAINT monthly_exam_schedules_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id);


--
-- Name: monthly_exam_schedules monthly_exam_schedules_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.monthly_exam_schedules
    ADD CONSTRAINT monthly_exam_schedules_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id);


--
-- Name: notification_logs notification_logs_notification_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_logs
    ADD CONSTRAINT notification_logs_notification_id_fkey FOREIGN KEY (notification_id) REFERENCES public.notifications(id) ON DELETE CASCADE;


--
-- Name: notification_logs notification_logs_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_logs
    ADD CONSTRAINT notification_logs_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.parents(id) ON DELETE CASCADE;


--
-- Name: notifications notifications_sender_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_sender_user_id_fkey FOREIGN KEY (sender_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: notifications notifications_target_grade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_target_grade_id_fkey FOREIGN KEY (target_grade_id) REFERENCES public.grades(id) ON DELETE SET NULL;


--
-- Name: notifications notifications_target_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_target_section_id_fkey FOREIGN KEY (target_section_id) REFERENCES public.sections(id) ON DELETE SET NULL;


--
-- Name: parent_devices parent_devices_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parent_devices
    ADD CONSTRAINT parent_devices_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.parents(id) ON DELETE CASCADE;


--
-- Name: payroll_records payroll_records_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payroll_records
    ADD CONSTRAINT payroll_records_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE CASCADE;


--
-- Name: print_archive print_archive_printed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.print_archive
    ADD CONSTRAINT print_archive_printed_by_fkey FOREIGN KEY (printed_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: receipts receipts_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.receipts
    ADD CONSTRAINT receipts_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id);


--
-- Name: receipts receipts_installment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.receipts
    ADD CONSTRAINT receipts_installment_id_fkey FOREIGN KEY (installment_id) REFERENCES public.fee_installments(id) ON DELETE SET NULL;


--
-- Name: receipts receipts_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.receipts
    ADD CONSTRAINT receipts_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: sections sections_grade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT sections_grade_id_fkey FOREIGN KEY (grade_id) REFERENCES public.grades(id) ON DELETE CASCADE;


--
-- Name: student_academic_history student_academic_history_academic_year_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_academic_history
    ADD CONSTRAINT student_academic_history_academic_year_id_fkey FOREIGN KEY (academic_year_id) REFERENCES public.academic_years(id);


--
-- Name: student_academic_history student_academic_history_grade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_academic_history
    ADD CONSTRAINT student_academic_history_grade_id_fkey FOREIGN KEY (grade_id) REFERENCES public.grades(id);


--
-- Name: student_academic_history student_academic_history_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_academic_history
    ADD CONSTRAINT student_academic_history_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id);


--
-- Name: student_academic_history student_academic_history_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_academic_history
    ADD CONSTRAINT student_academic_history_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- Name: student_documents student_documents_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_documents
    ADD CONSTRAINT student_documents_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- Name: student_fees student_fees_academic_year_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_fees
    ADD CONSTRAINT student_fees_academic_year_id_fkey FOREIGN KEY (academic_year_id) REFERENCES public.academic_years(id) ON DELETE CASCADE;


--
-- Name: student_fees student_fees_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_fees
    ADD CONSTRAINT student_fees_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- Name: students students_academic_year_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_academic_year_id_fkey FOREIGN KEY (academic_year_id) REFERENCES public.academic_years(id);


--
-- Name: students students_grade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_grade_id_fkey FOREIGN KEY (grade_id) REFERENCES public.grades(id);


--
-- Name: students students_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.parents(id) ON DELETE SET NULL;


--
-- Name: students students_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id);


--
-- Name: system_audit_logs system_audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_audit_logs
    ADD CONSTRAINT system_audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: teacher_subject_sections teacher_subject_sections_academic_year_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_subject_sections
    ADD CONSTRAINT teacher_subject_sections_academic_year_id_fkey FOREIGN KEY (academic_year_id) REFERENCES public.academic_years(id) ON DELETE CASCADE;


--
-- Name: teacher_subject_sections teacher_subject_sections_grade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_subject_sections
    ADD CONSTRAINT teacher_subject_sections_grade_id_fkey FOREIGN KEY (grade_id) REFERENCES public.grades(id) ON DELETE CASCADE;


--
-- Name: teacher_subject_sections teacher_subject_sections_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_subject_sections
    ADD CONSTRAINT teacher_subject_sections_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id) ON DELETE CASCADE;


--
-- Name: teacher_subject_sections teacher_subject_sections_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_subject_sections
    ADD CONSTRAINT teacher_subject_sections_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id) ON DELETE CASCADE;


--
-- Name: teacher_subject_sections teacher_subject_sections_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_subject_sections
    ADD CONSTRAINT teacher_subject_sections_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.employees(id) ON DELETE CASCADE;


--
-- Name: term_exam_scores term_exam_scores_academic_year_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.term_exam_scores
    ADD CONSTRAINT term_exam_scores_academic_year_id_fkey FOREIGN KEY (academic_year_id) REFERENCES public.academic_years(id);


--
-- Name: term_exam_scores term_exam_scores_grade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.term_exam_scores
    ADD CONSTRAINT term_exam_scores_grade_id_fkey FOREIGN KEY (grade_id) REFERENCES public.grades(id);


--
-- Name: term_exam_scores term_exam_scores_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.term_exam_scores
    ADD CONSTRAINT term_exam_scores_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id);


--
-- Name: term_exam_scores term_exam_scores_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.term_exam_scores
    ADD CONSTRAINT term_exam_scores_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- Name: term_exam_scores term_exam_scores_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.term_exam_scores
    ADD CONSTRAINT term_exam_scores_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id);


--
-- Name: users users_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE SET NULL;


--
-- Name: users users_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- Name: weekly_schedules weekly_schedules_academic_year_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weekly_schedules
    ADD CONSTRAINT weekly_schedules_academic_year_id_fkey FOREIGN KEY (academic_year_id) REFERENCES public.academic_years(id);


--
-- Name: weekly_schedules weekly_schedules_grade_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weekly_schedules
    ADD CONSTRAINT weekly_schedules_grade_id_fkey FOREIGN KEY (grade_id) REFERENCES public.grades(id);


--
-- Name: weekly_schedules weekly_schedules_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weekly_schedules
    ADD CONSTRAINT weekly_schedules_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id);


--
-- Name: weekly_schedules weekly_schedules_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weekly_schedules
    ADD CONSTRAINT weekly_schedules_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id);


--
-- Name: weekly_schedules weekly_schedules_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weekly_schedules
    ADD CONSTRAINT weekly_schedules_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.employees(id);


--
-- PostgreSQL database dump complete
--

\unrestrict 91tjqtcIMKyQsgnvxQUCcXNinwyJlMnjT4BUJIBH9SxhXo1yVK6zJOz4921Nsc7

