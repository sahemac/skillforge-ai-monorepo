import { BaseEntity } from '@skillforge-ai/core';

export enum ProjectStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
}

export enum ProjectType {
  FULL_TIME = 'full_time',
  PART_TIME = 'part_time',
  CONTRACT = 'contract',
  FREELANCE = 'freelance',
  INTERNSHIP = 'internship',
}

export enum ExperienceLevel {
  ENTRY = 'entry',
  JUNIOR = 'junior',
  MIDDLE = 'middle',
  SENIOR = 'senior',
  LEAD = 'lead',
  PRINCIPAL = 'principal',
}

export interface ProjectRequirement {
  skill: string;
  level: 'basic' | 'intermediate' | 'advanced' | 'expert';
  required: boolean;
  yearsOfExperience?: number;
}

export interface ProjectProps {
  title: string;
  description: string;
  companyId: string;
  type: ProjectType;
  status: ProjectStatus;
  experienceLevel: ExperienceLevel;
  location?: string;
  remote: boolean;
  salary?: {
    min?: number;
    max?: number;
    currency: string;
    period: 'hourly' | 'monthly' | 'yearly';
  };
  requirements: ProjectRequirement[];
  benefits?: string[];
  applicationDeadline?: Date;
  startDate?: Date;
  duration?: string;
  applicationsCount: number;
  viewsCount: number;
}

export class Project extends BaseEntity<string> {
  private _title: string;
  private _description: string;
  private _companyId: string;
  private _type: ProjectType;
  private _status: ProjectStatus;
  private _experienceLevel: ExperienceLevel;
  private _location?: string;
  private _remote: boolean;
  private _salary?: ProjectProps['salary'];
  private _requirements: ProjectRequirement[];
  private _benefits?: string[];
  private _applicationDeadline?: Date;
  private _startDate?: Date;
  private _duration?: string;
  private _applicationsCount: number;
  private _viewsCount: number;

  constructor(id: string, props: ProjectProps, createdAt?: Date) {
    super(id, createdAt);

    this._title = props.title;
    this._description = props.description;
    this._companyId = props.companyId;
    this._type = props.type;
    this._status = props.status;
    this._experienceLevel = props.experienceLevel;
    this._location = props.location;
    this._remote = props.remote;
    this._salary = props.salary;
    this._requirements = props.requirements;
    this._benefits = props.benefits;
    this._applicationDeadline = props.applicationDeadline;
    this._startDate = props.startDate;
    this._duration = props.duration;
    this._applicationsCount = props.applicationsCount;
    this._viewsCount = props.viewsCount;
  }

  get title(): string { return this._title; }
  get description(): string { return this._description; }
  get companyId(): string { return this._companyId; }
  get type(): ProjectType { return this._type; }
  get status(): ProjectStatus { return this._status; }
  get experienceLevel(): ExperienceLevel { return this._experienceLevel; }
  get location(): string | undefined { return this._location; }
  get remote(): boolean { return this._remote; }
  get salary(): ProjectProps['salary'] { return this._salary; }
  get requirements(): ProjectRequirement[] { return [...this._requirements]; }
  get benefits(): string[] | undefined { return this._benefits ? [...this._benefits] : undefined; }
  get applicationDeadline(): Date | undefined { return this._applicationDeadline; }
  get startDate(): Date | undefined { return this._startDate; }
  get duration(): string | undefined { return this._duration; }
  get applicationsCount(): number { return this._applicationsCount; }
  get viewsCount(): number { return this._viewsCount; }

  public updateDetails(updates: Partial<ProjectProps>): void {
    if (updates.title) this._title = updates.title;
    if (updates.description) this._description = updates.description;
    if (updates.type) this._type = updates.type;
    if (updates.experienceLevel) this._experienceLevel = updates.experienceLevel;
    if (updates.location !== undefined) this._location = updates.location;
    if (updates.remote !== undefined) this._remote = updates.remote;
    if (updates.salary !== undefined) this._salary = updates.salary;
    if (updates.requirements) this._requirements = updates.requirements;
    if (updates.benefits !== undefined) this._benefits = updates.benefits;
    if (updates.applicationDeadline !== undefined) this._applicationDeadline = updates.applicationDeadline;
    if (updates.startDate !== undefined) this._startDate = updates.startDate;
    if (updates.duration !== undefined) this._duration = updates.duration;
    this.touch();
  }

  public publish(): void {
    if (this._status === ProjectStatus.DRAFT) {
      this._status = ProjectStatus.PUBLISHED;
      this.touch();
    }
  }

  public pause(): void {
    if (this._status === ProjectStatus.PUBLISHED) {
      this._status = ProjectStatus.PAUSED;
      this.touch();
    }
  }

  public resume(): void {
    if (this._status === ProjectStatus.PAUSED) {
      this._status = ProjectStatus.PUBLISHED;
      this.touch();
    }
  }

  public complete(): void {
    this._status = ProjectStatus.COMPLETED;
    this.touch();
  }

  public cancel(): void {
    this._status = ProjectStatus.CANCELLED;
    this.touch();
  }

  public incrementViews(): void {
    this._viewsCount += 1;
    this.touch();
  }

  public incrementApplications(): void {
    this._applicationsCount += 1;
    this.touch();
  }

  public isActive(): boolean {
    return this._status === ProjectStatus.PUBLISHED;
  }

  public isExpired(): boolean {
    if (!this._applicationDeadline) return false;
    return new Date() > this._applicationDeadline;
  }

  public getRequiredSkills(): string[] {
    return this._requirements
      .filter(req => req.required)
      .map(req => req.skill);
  }

  public getOptionalSkills(): string[] {
    return this._requirements
      .filter(req => !req.required)
      .map(req => req.skill);
  }

  public getSalaryRange(): string | null {
    if (!this._salary) return null;

    const { min, max, currency, period } = this._salary;
    const formatCurrency = (amount: number) => `${currency} ${amount.toLocaleString()}`;

    if (min && max) {
      return `${formatCurrency(min)} - ${formatCurrency(max)} ${period}`;
    }
    if (min) {
      return `From ${formatCurrency(min)} ${period}`;
    }
    if (max) {
      return `Up to ${formatCurrency(max)} ${period}`;
    }

    return null;
  }

  public toJSON(): Record<string, any> {
    return {
      ...super.toJSON(),
      title: this._title,
      description: this._description,
      companyId: this._companyId,
      type: this._type,
      status: this._status,
      experienceLevel: this._experienceLevel,
      location: this._location,
      remote: this._remote,
      salary: this._salary,
      requirements: this._requirements,
      benefits: this._benefits,
      applicationDeadline: this._applicationDeadline,
      startDate: this._startDate,
      duration: this._duration,
      applicationsCount: this._applicationsCount,
      viewsCount: this._viewsCount,
    };
  }
}
