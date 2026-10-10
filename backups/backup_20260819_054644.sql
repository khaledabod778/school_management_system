--
-- PostgreSQL database dump
--

\restrict Zjw7kxv8kcyOSN4tFgUw791OZoaknMjMif8jsd5nWyCQenziRgAo2uh3EgPpwkt

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
1	2026-2027	1448هـ	2026-09-01	2027-06-30	t	current	f	\N	\N	2026-08-19 04:34:51.810578	\N
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
\.


--
-- Data for Name: daily_attendance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.daily_attendance (id, student_id, academic_year_id, grade_id, section_id, attendance_date, status, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: employee_allowances_deductions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employee_allowances_deductions (id, employee_id, type, amount, reason, date, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: employee_loans; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employee_loans (id, employee_id, total_loan_amount, monthly_deduction, status, loan_date, reason, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: employees; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employees (id, full_name, job_title, qualification, primary_phone, secondary_phone, gender, marital_status, address, status, national_id, id_issue_place, id_issue_date, birth_date, birth_village, birth_district, birth_governorate, contract_start_date, contract_end_date, basic_salary, payment_method, bank_account_number, created_at, updated_at) FROM stdin;
1	مدير النظام	مدير نظام	\N	0000000000	\N	\N	\N	\N	نشط	\N	\N	\N	\N	\N	\N	\N	\N	\N	0.00	نقداً	\N	2026-08-19 04:34:51.766994	\N
\.


--
-- Data for Name: expense_vouchers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expense_vouchers (id, voucher_number, expense_category, beneficiary_name, amount, payment_date, payment_method, invoice_number, notes, created_by_user_id, status, cancellation_reason, cancelled_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: fee_installments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fee_installments (id, student_fee_id, installment_type, installment_number, installment_name, amount, due_date, is_paid, paid_amount, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: fee_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fee_types (id, fee_name, created_at, updated_at) FROM stdin;
1	رسوم دراسية	2026-08-19 04:34:51.866558	\N
2	رسوم تسجيل	2026-08-19 04:34:51.866558	\N
3	زي مدرسي	2026-08-19 04:34:51.866558	\N
4	كتب	2026-08-19 04:34:51.866558	\N
5	مواصلات	2026-08-19 04:34:51.866558	\N
6	أنشطة	2026-08-19 04:34:51.866558	\N
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
\.


--
-- Data for Name: grades; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.grades (id, grade_name, stage_name, max_capacity, created_at, updated_at) FROM stdin;
1	الأول الأساسي	الابتدائي	30	2026-08-19 04:34:51.815504	\N
2	الثاني الأساسي	الابتدائي	30	2026-08-19 04:34:51.815504	\N
3	الثالث الأساسي	الابتدائي	30	2026-08-19 04:34:51.815504	\N
4	الرابع الأساسي	الابتدائي	30	2026-08-19 04:34:51.815504	\N
5	الخامس الأساسي	الابتدائي	30	2026-08-19 04:34:51.815504	\N
6	السادس الأساسي	الابتدائي	30	2026-08-19 04:34:51.815504	\N
7	السابع الأساسي	الإعدادي	35	2026-08-19 04:34:51.815504	\N
8	الثامن الأساسي	الإعدادي	35	2026-08-19 04:34:51.815504	\N
9	التاسع الأساسي	الإعدادي	35	2026-08-19 04:34:51.815504	\N
10	الأول الثانوي	الثانوي	40	2026-08-19 04:34:51.815504	\N
11	الثاني الثانوي	الثانوي	40	2026-08-19 04:34:51.815504	\N
12	الثالث الثانوي	الثانوي	40	2026-08-19 04:34:51.815504	\N
\.


--
-- Data for Name: homeworks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.homeworks (id, academic_year_id, grade_id, section_id, subject_id, homework_date, title, description, due_date, created_at, updated_at) FROM stdin;
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
\.


--
-- Data for Name: monthly_exam_schedules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.monthly_exam_schedules (id, academic_year_id, term, month, grade_id, section_id, subject_id, exam_date, day_name, period_number, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: notification_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notification_logs (id, notification_id, parent_id, sent_at, delivery_status, read_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notifications (id, title, message, notification_type, sender_user_id, target_type, target_grade_id, target_section_id, scheduled_at, sent_at, is_active, created_at, updated_at) FROM stdin;
1	igh	uu	عام	1	all	\N	\N	\N	2026-08-19 05:43:13.523681	t	2026-08-19 05:43:13.52159	2026-08-19 05:43:13.52159
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
\.


--
-- Data for Name: payroll_records; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payroll_records (id, employee_id, month, year, basic_salary, total_allowances, total_deductions, loan_deduction, net_salary, payment_status, payment_date, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.permissions (id, module_name, permission_key) FROM stdin;
1	لوحة التحكم	module_0
2	الطلاب	module_1
3	أولياء الأمور	module_2
4	الحضور	module_3
5	الدرجات	module_4
6	الواجبات	module_5
7	الجداول	module_6
8	الرسوم	module_7
9	السندات	module_8
10	الرواتب	module_9
11	المصروفات	module_10
12	الموظفين	module_11
13	المستخدمين	module_12
14	الصلاحيات	module_13
15	الإعدادات	module_14
16	التقارير	module_15
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
\.


--
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.role_permissions (role_id, permission_id, can_view, can_add, can_edit, can_delete, can_print, can_cancel) FROM stdin;
1	1	t	t	t	t	t	t
1	2	t	t	t	t	t	t
1	3	t	t	t	t	t	t
1	4	t	t	t	t	t	t
1	5	t	t	t	t	t	t
1	6	t	t	t	t	t	t
1	7	t	t	t	t	t	t
1	8	t	t	t	t	t	t
1	9	t	t	t	t	t	t
1	10	t	t	t	t	t	t
1	11	t	t	t	t	t	t
1	12	t	t	t	t	t	t
1	13	t	t	t	t	t	t
1	14	t	t	t	t	t	t
1	15	t	t	t	t	t	t
1	16	t	t	t	t	t	t
6	4	t	t	t	f	t	f
6	5	t	t	t	f	t	f
6	6	t	t	t	f	t	f
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, role_name, description, created_at, updated_at) FROM stdin;
1	مدير النظام	صلاحيات كاملة للنظام	2026-08-19 04:34:51.728499	\N
2	مدير عام	إدارة شاملة للمدرسة	2026-08-19 04:34:51.728499	\N
3	محاسب	إدارة الشؤون المالية	2026-08-19 04:34:51.728499	\N
4	مدخل بيانات	إدخال البيانات	2026-08-19 04:34:51.728499	\N
5	أخصائي اجتماعي	متابعة الطلاب	2026-08-19 04:34:51.728499	\N
6	معلم	رصد الدرجات والحضور	2026-08-19 04:34:51.728499	\N
\.


--
-- Data for Name: school_info; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.school_info (id, school_name_ar, school_name_en, principal_name, license_number, phone_primary, phone_secondary, email, address_detail, logo_url, header_footer_url, terms_and_conditions, created_at, updated_at) FROM stdin;
1	مدرسة النور الأهلية	Al-Noor Private School	\N	\N	\N	\N	\N	\N	\N	\N	شروط وأحكام المدرسة	2026-08-19 04:34:51.874324	2026-08-19 05:07:44.465472
\.


--
-- Data for Name: sections; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sections (id, grade_id, section_name, capacity, created_at, updated_at) FROM stdin;
1	1	أ	30	2026-08-19 04:34:51.815504	\N
2	1	ب	30	2026-08-19 04:34:51.815504	\N
3	1	ج	30	2026-08-19 04:34:51.815504	\N
4	2	أ	30	2026-08-19 04:34:51.815504	\N
5	2	ب	30	2026-08-19 04:34:51.815504	\N
6	2	ج	30	2026-08-19 04:34:51.815504	\N
7	3	أ	30	2026-08-19 04:34:51.815504	\N
8	3	ب	30	2026-08-19 04:34:51.815504	\N
9	3	ج	30	2026-08-19 04:34:51.815504	\N
10	4	أ	30	2026-08-19 04:34:51.815504	\N
11	4	ب	30	2026-08-19 04:34:51.815504	\N
12	4	ج	30	2026-08-19 04:34:51.815504	\N
13	5	أ	30	2026-08-19 04:34:51.815504	\N
14	5	ب	30	2026-08-19 04:34:51.815504	\N
15	5	ج	30	2026-08-19 04:34:51.815504	\N
16	6	أ	30	2026-08-19 04:34:51.815504	\N
17	6	ب	30	2026-08-19 04:34:51.815504	\N
18	6	ج	30	2026-08-19 04:34:51.815504	\N
19	7	أ	35	2026-08-19 04:34:51.815504	\N
20	7	ب	35	2026-08-19 04:34:51.815504	\N
21	7	ج	35	2026-08-19 04:34:51.815504	\N
22	8	أ	35	2026-08-19 04:34:51.815504	\N
23	8	ب	35	2026-08-19 04:34:51.815504	\N
24	8	ج	35	2026-08-19 04:34:51.815504	\N
25	9	أ	35	2026-08-19 04:34:51.815504	\N
26	9	ب	35	2026-08-19 04:34:51.815504	\N
27	9	ج	35	2026-08-19 04:34:51.815504	\N
28	10	أ	40	2026-08-19 04:34:51.815504	\N
29	10	ب	40	2026-08-19 04:34:51.815504	\N
30	10	ج	40	2026-08-19 04:34:51.815504	\N
31	11	أ	40	2026-08-19 04:34:51.815504	\N
32	11	ب	40	2026-08-19 04:34:51.815504	\N
33	11	ج	40	2026-08-19 04:34:51.815504	\N
34	12	أ	40	2026-08-19 04:34:51.815504	\N
35	12	ب	40	2026-08-19 04:34:51.815504	\N
36	12	ج	40	2026-08-19 04:34:51.815504	\N
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
\.


--
-- Data for Name: student_fees; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.student_fees (id, student_id, academic_year_id, previous_debt, current_year_fees, discount_amount, net_total_required, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: students; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.students (id, student_number, full_name, mother_name, gender, nationality, status, enrollment_type, student_status_reason, birth_date, birth_village, birth_district, birth_governorate, transferred_from_school, transferred_district, transferred_governorate, transfer_date, academic_year_id, grade_id, section_id, parent_id, photo_url, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: subjects; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.subjects (id, subject_name, min_pass_score, max_score, created_at, updated_at) FROM stdin;
1	القرآن الكريم	50.00	100.00	2026-08-19 04:34:51.85931	\N
2	التربية الإسلامية	50.00	100.00	2026-08-19 04:34:51.85931	\N
3	اللغة العربية	50.00	100.00	2026-08-19 04:34:51.85931	\N
4	اللغة الإنجليزية	50.00	100.00	2026-08-19 04:34:51.85931	\N
5	الرياضيات	50.00	100.00	2026-08-19 04:34:51.85931	\N
6	العلوم	50.00	100.00	2026-08-19 04:34:51.85931	\N
7	الدراسات الاجتماعية	50.00	100.00	2026-08-19 04:34:51.85931	\N
8	الحاسوب	50.00	100.00	2026-08-19 04:34:51.85931	\N
9	التربية الفنية	50.00	100.00	2026-08-19 04:34:51.85931	\N
10	التربية البدنية	50.00	100.00	2026-08-19 04:34:51.85931	\N
\.


--
-- Data for Name: system_audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_audit_logs (id, user_id, module_name, operation_type, record_id, old_values, new_values, ip_address, device_name, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: teacher_subject_sections; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.teacher_subject_sections (id, academic_year_id, grade_id, section_id, subject_id, teacher_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: term_exam_scores; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.term_exam_scores (id, student_id, academic_year_id, grade_id, section_id, subject_id, term, exam_score, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, employee_id, username, password_hash, role_id, profile_image, phone, email, status, last_login, last_password_change, created_at, updated_at) FROM stdin;
1	1	admin	1194cc0dc63d50cea0205288220bb873$744c2beb178d50579fce7c99a969429a5d57bac3108edc31bfdae2a22569d92e	1	\N	\N	\N	نشط	2026-08-19 05:38:40.098609	\N	2026-08-19 04:34:51.766994	2026-08-19 05:38:40.063687
\.


--
-- Data for Name: weekly_schedules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.weekly_schedules (id, academic_year_id, term, grade_id, section_id, day_of_week, period_number, subject_id, teacher_id, created_at, updated_at) FROM stdin;
\.


--
-- Name: academic_years_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.academic_years_id_seq', 1, true);


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

SELECT pg_catalog.setval('public.behavioral_records_id_seq', 1, false);


--
-- Name: daily_attendance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.daily_attendance_id_seq', 1, false);


--
-- Name: employee_allowances_deductions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.employee_allowances_deductions_id_seq', 1, false);


--
-- Name: employee_loans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.employee_loans_id_seq', 1, false);


--
-- Name: employees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.employees_id_seq', 1, true);


--
-- Name: expense_vouchers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.expense_vouchers_id_seq', 1, false);


--
-- Name: fee_installments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fee_installments_id_seq', 1, false);


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

SELECT pg_catalog.setval('public.grade_fee_structures_id_seq', 1, false);


--
-- Name: grades_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.grades_id_seq', 12, true);


--
-- Name: homeworks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.homeworks_id_seq', 1, false);


--
-- Name: import_export_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.import_export_logs_id_seq', 1, false);


--
-- Name: monthly_evaluations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.monthly_evaluations_id_seq', 1, false);


--
-- Name: monthly_exam_schedules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.monthly_exam_schedules_id_seq', 1, false);


--
-- Name: notification_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notification_logs_id_seq', 1, false);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notifications_id_seq', 1, true);


--
-- Name: parent_devices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.parent_devices_id_seq', 1, false);


--
-- Name: parents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.parents_id_seq', 1, false);


--
-- Name: payroll_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payroll_records_id_seq', 1, false);


--
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.permissions_id_seq', 16, true);


--
-- Name: print_archive_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.print_archive_id_seq', 1, false);


--
-- Name: receipts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.receipts_id_seq', 1, false);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 6, true);


--
-- Name: school_info_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.school_info_id_seq', 1, true);


--
-- Name: sections_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sections_id_seq', 36, true);


--
-- Name: student_academic_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_academic_history_id_seq', 1, false);


--
-- Name: student_documents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_documents_id_seq', 1, false);


--
-- Name: student_fees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.student_fees_id_seq', 1, false);


--
-- Name: students_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.students_id_seq', 1, false);


--
-- Name: subjects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.subjects_id_seq', 10, true);


--
-- Name: system_audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.system_audit_logs_id_seq', 1, false);


--
-- Name: teacher_subject_sections_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.teacher_subject_sections_id_seq', 1, false);


--
-- Name: term_exam_scores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.term_exam_scores_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: weekly_schedules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.weekly_schedules_id_seq', 1, false);


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

\unrestrict Zjw7kxv8kcyOSN4tFgUw791OZoaknMjMif8jsd5nWyCQenziRgAo2uh3EgPpwkt

