import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router, convertToParamMap } from '@angular/router';

import { of } from 'rxjs';

import { ApiService } from '../services/api.service';
import { UserService } from '../services/user.service';
import { ApiServiceMock } from '../services/api.service.mock';
import { UserServiceMock } from '../services/user.service.mock';

import { ResetPasswordComponent } from './reset-password.component';

describe('ResetPasswordComponent', () => {
  let component: ResetPasswordComponent;
  let fixture: ComponentFixture<ResetPasswordComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
        imports: [ FormsModule, ReactiveFormsModule ],
        declarations: [ ResetPasswordComponent ],
        providers: [
            { provide: ApiService, useValue: new ApiServiceMock() },
            {
                provide: ActivatedRoute, useValue: {
                    params: of(<{ token: string }>{ token: 'check12check12' }).map(convertToParamMap)
                }
            },
            {
                provide: Router, useValue: {}
            },
            {
                provide: UserService, useValue: new UserServiceMock()
            },
        ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ResetPasswordComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
